from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import os
import tempfile
import threading
import yaml
from datetime import datetime
from shot_detector import ShotDetector
from contest import ContestAnalyzer
from generate_pdf import generate_basketball_pdf

# Load environment configuration
env = yaml.load(open('config.yaml', 'r'), Loader=yaml.SafeLoader)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = env['upload_path']
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Create necessary directories
RESULTS_DIR = os.path.join(app.config['UPLOAD_FOLDER'], "results")
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

class VideoProcessor:
    def __init__(self, socket):
        self.socket = socket
        self.shots_detected = 0
        self.shots_made = 0
        self.made_shots_path = None
        self.missed_shots_path = None
        self.contest_results = None
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.analysis_dir = os.path.join(RESULTS_DIR, self.timestamp)
        os.makedirs(self.analysis_dir, exist_ok=True)

    def on_shot_detect(self, start_time: float, end_time: float, made: bool):
        # Emit real-time shot detection event
        self.socket.emit('shooting_detected', {
            'success': True,
            'start_time': start_time,
            'end_time': end_time,
            'made': made
        })

    def on_detection_complete(self, attempts: int, makes: int, made_path: str, missed_path: str):
        self.shots_detected = attempts
        self.shots_made = makes
        self.made_shots_path = made_path
        self.missed_shots_path = missed_path

        try:
            # Process contest analysis
            analyzer = ContestAnalyzer()
            
            # Analyze made shots
            if made_path and os.path.exists(made_path):
                made_contest_results = analyzer.analyze_video(made_path)
            else:
                made_contest_results = {"contested_shots": 0, "uncontested_shots": 0}
            
            # Analyze missed shots
            if missed_path and os.path.exists(missed_path):
                missed_contest_results = analyzer.analyze_video(missed_path)
            else:
                missed_contest_results = {"contested_shots": 0, "uncontested_shots": 0}

            # Convert absolute paths to relative paths for frontend
            made_video_path = os.path.relpath(made_path, RESULTS_DIR) if made_path else None
            missed_video_path = os.path.relpath(missed_path, RESULTS_DIR) if missed_path else None

            # Emit complete results
            self.socket.emit('processing_complete', {
                'attempts': attempts,
                'makes': makes,
                'made_contested': made_contest_results["contested_shots"],
                'made_uncontested': made_contest_results["uncontested_shots"],
                'missed_contested': missed_contest_results["contested_shots"],
                'missed_uncontested': missed_contest_results["uncontested_shots"],
                'made_shots_video': made_video_path,
                'missed_shots_video': missed_video_path
            })
        except Exception as e:
            print(f"Error in contest analysis: {str(e)}")
            # Emit basic results without contest analysis
            self.socket.emit('processing_complete', {
                'attempts': attempts,
                'makes': makes,
                'made_contested': 0,
                'made_uncontested': makes,
                'missed_contested': 0,
                'missed_uncontested': attempts - makes,
                'made_shots_video': made_video_path if 'made_video_path' in locals() else None,
                'missed_shots_video': missed_video_path if 'missed_video_path' in locals() else None
            })

def process_video(video_path):
    try:
        processor = VideoProcessor(socketio)
        detector = ShotDetector(
            video_path=video_path,
            on_detect=processor.on_shot_detect,
            on_complete=processor.on_detection_complete,
            show_vid=False
        )
    except Exception as e:
        socketio.emit('error', {'message': str(e)})
    finally:
        # Clean up temporary file after processing
        if os.path.exists(video_path) and video_path.startswith(app.config['UPLOAD_FOLDER']):
            os.remove(video_path)

@app.route('/upload', methods=['POST'])
def upload_video():
    print('upload_video')
    try:
        file = request.files['video']
        video_path = os.path.join(app.config['UPLOAD_FOLDER'], f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
        file.save(video_path)

        # Process video in a separate thread
        thread = threading.Thread(target=process_video, args=(video_path,))
        thread.daemon = True
        thread.start()

        return jsonify({'message': 'Processing started successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/video/<path:filename>')
def serve_video(filename):
    return send_from_directory(RESULTS_DIR, filename)

@app.route('/generate-report', methods=['POST'])
def generate_report():
    print('generate report')
    try:
        data = request.json
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], "basketball_game_report.pdf")

        # Extract required data from the frontend request
        game_summary = data.get("game_summary", {})
        field_goals_stats = data.get("field_goals_stats", {})
        shot_types_stats = data.get("shot_types_stats", {})
        shot_zones_stats = data.get("shot_zones_stats", {})
        match = data.get("match", True)
        quarter_scores = data.get("quarter_scores", {})
        quarter_percentages = data.get("quarter_percentages", {})
        shot_data = data.get("shot_data", [])
        court_image_path = "court_img.png"

        # Generate PDF
        generate_basketball_pdf(
            file_path,
            game_summary,
            field_goals_stats,
            shot_types_stats,
            shot_zones_stats,
            match,
            quarter_scores,
            quarter_percentages,
            shot_data,
            court_image_path,
        )
        return send_file(file_path, as_attachment=True, mimetype="application/pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001) 