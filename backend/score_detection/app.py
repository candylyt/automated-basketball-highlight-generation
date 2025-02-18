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
import json

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

class ResultManager:
    def __init__(self, socket):
        self.socket = socket
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.analysis_dir = os.path.join(RESULTS_DIR, self.timestamp)
        os.makedirs(self.analysis_dir, exist_ok=True)
        self.statistics = {
            'attempts': 0,
            'makes': 0,
            'made_contested': 0,
            'made_uncontested': 0,
            'missed_contested': 0,
            'missed_uncontested': 0,
            'made_shots_video': None,
            'missed_shots_video': None
        }

    def on_shot_detect(self, start_time: float, end_time: float, made: bool):
        self.socket.emit('shooting_detected', {
            'success': True,
            'start_time': start_time,
            'end_time': end_time,
            'made': made
        })

    def on_detection_complete(self, attempts: int, makes: int, made_path: str, missed_path: str):
        self.statistics['attempts'] = attempts
        self.statistics['makes'] = makes
        
        try:
            # Process contest analysis
            analyzer = ContestAnalyzer()
            
            # Analyze made shots
            if made_path and os.path.exists(made_path):
                made_contest_results = analyzer.analyze_video(made_path)
                self.statistics['made_contested'] = made_contest_results["contested_shots"]
                self.statistics['made_uncontested'] = made_contest_results["uncontested_shots"]
            
            # Analyze missed shots
            if missed_path and os.path.exists(missed_path):
                missed_contest_results = analyzer.analyze_video(missed_path)
                self.statistics['missed_contested'] = missed_contest_results["contested_shots"]
                self.statistics['missed_uncontested'] = missed_contest_results["uncontested_shots"]

            # Convert absolute paths to relative paths for frontend
            self.statistics['made_shots_video'] = os.path.relpath(made_path, RESULTS_DIR) if made_path else None
            self.statistics['missed_shots_video'] = os.path.relpath(missed_path, RESULTS_DIR) if missed_path else None

            # Store statistics in a file for later retrieval
            stats_file = os.path.join(self.analysis_dir, 'statistics.json')
            with open(stats_file, 'w') as f:
                json.dump(self.statistics, f)

            # Emit complete results
            self.socket.emit('processing_complete', self.statistics)
            
        except Exception as e:
            print(f"Error in contest analysis: {str(e)}")
            # Emit basic results without contest analysis
            self.socket.emit('processing_complete', self.statistics)

def process_video(video_path):
    try:
        result_manager = ResultManager(socketio)
        detector = ShotDetector(
            video_path=video_path,
            on_detect=result_manager.on_shot_detect,
            on_complete=result_manager.on_detection_complete,
            show_vid=False
        )
        detector.run()  # Start the video processing
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

@app.route('/get_statistics/<timestamp>', methods=['GET'])
def get_statistics(timestamp):
    try:
        stats_file = os.path.join(RESULTS_DIR, timestamp, 'statistics.json')
        if os.path.exists(stats_file):
            with open(stats_file, 'r') as f:
                return jsonify(json.load(f))
        return jsonify({'error': 'Statistics not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    socketio.run(app, debug=True, port=5001) 