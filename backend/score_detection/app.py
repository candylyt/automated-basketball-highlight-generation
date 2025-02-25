from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO
from shot_detector import ShotDetector
from generate_pdf import generate_basketball_pdf
from flask_cors import CORS
import threading
import yaml
import os
import time

env = yaml.load(open('config.yaml', 'r'), Loader=yaml.SafeLoader)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = env['upload_path']
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def process_video(video_path):
    def on_detection(start_time, end_time, success):
        socketio.emit('shooting_detected', {
            'start_time' : start_time,
            'end_time' : end_time,
            'success': success
        })

    def on_complete(attempts, makes):
        socketio.emit('processing_complete', {
            'attempts' : attempts,
            'makes' : makes
        })

    ShotDetector(video_path, on_detection, on_complete, show_vid=False)

@app.route('/upload' , methods=['POST'])
def upload_video():
    print('upload_video')
    file = request.files['video']
    video_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    file.save(video_path)

    thread = threading.Thread(target=process_video, args=(video_path, ))
    thread.daemon = True
    thread.start()

    return jsonify({'message' : 'Processing started successfully'})
    
@app.route('/generate-report', methods=['POST'])
def generate_report():
    print('generate report')
    try:
        data = request.json  # Receive JSON data from frontend

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
        court_image_path = "court_img.png"  # Ensure this file exists in your backend

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
    socketio.run(app, debug=True, port=env['flask_port'])