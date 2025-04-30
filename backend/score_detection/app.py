from flask import Flask, request, jsonify, send_file
from flask_socketio import SocketIO
from shot_detector import ShotDetector
from generate_pdf import generate_basketball_pdf
from flask_cors import CORS
import threading
import yaml
import os
import time
from match_handler import MatchHandler
import uuid
import json

from logger import (
    INFO,
    SOCKET,
    Logger
)



logger = Logger([
    INFO,
    SOCKET
])


env = yaml.load(open('config.yaml', 'r'), Loader=yaml.SafeLoader)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = env['upload_path']
app.config['REPORT_FOLDER'] = env['report_path']
app.config['DATA_FOLDER'] = env['data_path']
app.config['RESOURCE_FOLDER'] = env['resource_path']
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Callback functions for MatchHandler
def on_detection(run_id, start_time, end_time, success, team=None, video_id=1):
    '''
    {
        'start_time' :  str,   => time in 'hh:mm:ss' format
        'end_time' :    str,  
        'success' :     bool,
        'team' :        char[Optional],  => either 'A', 'B' if is_match is true or otherwise None
        'video_id' :    int,   => 1 or 2
    }
    
    '''

    data = {
        'run_id' : run_id,
        'start_time' : start_time,
        'end_time' : end_time,
        'success': success,
        'team' : team,
        'video_id' : video_id
        # 'location' : mapped_location
    }

    logger.log(SOCKET, f'[shooting_detected]    {data}')
    socketio.emit('shooting_detected', data)

def on_complete(run_id, report, is_match):
    '''
    if is_match:
    
    {
        'run_id' :      uuid
        'is_match' :    bool,
        
        'team_A': {
            'zone_makes':                       List[int],
            'zone_attempts':                    List[int],
            'zone_shooting_percentage':         List[float],
            'three_pt_makes':                   int,
            'three_pt_attempts':                int,
            'three_pt_shooting_percentage':     float,
            'two_pt_makes':                     int,
            'two_pt_attempts':                  int,
            'two_pt_shooting_percentage':       float,
            'paint_area_makes':                 int,
            'paint_area_attempts':              int,
            'paint_area_shooting_percentage':   float,
            'makes' :                           List[int],    # These 3 are by quarters
            'attempts' :                        List[int],
            'shooting_percentage' :             List[float],
            'total_makes' :                     int,
            'total_attempts' :                  int,
            'total_shooting_percentage' :       float
        },

        'team_B': {
            ...      # Similar
        }
        
    }

    Otherwise:

    {
        'run_id'   :        uuid,
        'is_match' :        bool,
        'zone_makes':       List[int],
        'zone_attempts':    List[int]
        ...                 # similar to above
    }
    '''
    logger.log(INFO, f'from handler: {report}, {is_match}')

    data = {
        'run_id' : run_id,
        'is_match' : is_match,
        **report
    }

    logger.log(SOCKET, f'[processing_complete]    {data}')
    
    socketio.emit('processing_complete', data)


@app.route('/upload' , methods=['POST'])
def upload_video():
    run_id = str(uuid.uuid4())
    
    logger.log(INFO, 'upload_video')

    video1 = request.files.get('video1')
    video2 = request.files.get('video2')
    video1_name = request.form.get('video1FileName')
    video2_name = request.form.get('video2FileName')

    points1 = request.form.get('points1')
    points2 = request.form.get('points2')

    image_dimensions1 = request.form.get('imageDimensions1')
    image_dimensions2 = request.form.get('imageDimensions2')

    logger.log(INFO, request.form)
    
    score_team_args = {
        "is_match" : request.form.get('isMatch') == 'true',
        "is_switched" : request.form.get('isSwitched') == 'true',
        "switch_time" : request.form.get('switchTimestamp'),
        "quarter_timestamps" : request.form.get('quarterTimestamps').split(',')
    }

    logger.log(INFO, score_team_args)
    
    video1_path = video2_path = None

    if video1_name:
        video1_path = os.path.join(app.config['UPLOAD_FOLDER'], video1_name)
        if video1:
            video1.save(video1_path)
    
    if video2_name:
        video2_path = os.path.join(app.config['UPLOAD_FOLDER'], video2_name)
        if video2:
            video2.save(video2_path)

     # Create MatchHandler
    handler = MatchHandler(
        video1_path=video1_path,
        video2_path=video2_path,
        quarter_timestamps=score_team_args["quarter_timestamps"],
        is_match=score_team_args["is_match"],
        is_switched=score_team_args["is_switched"],
        switch_time=score_team_args["switch_time"],
        points1=points1,
        points2=points2,
        image_dimensions1=image_dimensions1,
        image_dimensions2=image_dimensions2,
        on_detection_callback=on_detection,
        on_complete_callback=on_complete,
        run_id=run_id
    )

    thread = threading.Thread(target=handler.start_processing)
    thread.daemon = True
    thread.start()

    return jsonify({
        'run_id' : run_id,
        'message' : 'Processing started successfully'
    })
    
@app.route('/generate-report', methods=['POST'])
def generate_report():
    logger.log(INFO, 'generate report')
    try:
        # Extract required data from the frontend request
        run_id = request.json.get("run_id")

        if not run_id:
            return jsonify({"error": "run_id is required"}), 400
        
        file_path = os.path.join(app.config['REPORT_FOLDER'], f"{run_id}.pdf")
        stats_file_path = os.path.join(app.config['DATA_FOLDER'], f"{run_id}.json")
        
         # Check if the stats file exists
        if not os.path.exists(stats_file_path):
            return jsonify({"error": f"Data file for run_id {run_id} not found"}), 404

        # Load data from the JSON file
        with open(stats_file_path, "r") as json_file:
            report_data = json.load(json_file)

        court_image_path = os.path.join(app.config['RESOURCE_FOLDER'], "court_map.jpg")  # Ensure this file exists in your backend
        if not os.path.exists(court_image_path):
            return jsonify({"error": f"Data file for run_id {run_id} not found"}), 404

        # Generate PDF
        generate_basketball_pdf(
            file_path,
            court_image_path,
            **report_data
        )
        return send_file(file_path, as_attachment=True, mimetype="application/pdf")

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/check_file', methods=['POST'])
def check_file():
    """Check if a file with the given name exists on the server."""
    data = request.json
    filename = data.get('filename')

    if not filename:
        return jsonify({'error': 'Filename is required'}), 400

    # Sanitize filename to prevent directory traversal
    sanitized_filename = os.path.basename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], sanitized_filename)

    if os.path.exists(file_path):
        return jsonify({'exists': True})
    else:
        return jsonify({'exists': False})


if __name__ == "__main__":

    socketio.run(app, debug=True, port=env['flask_port'])