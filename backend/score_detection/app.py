from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from shot_detector import ShotDetector
from flask_cors import CORS
import threading
import yaml
import os

env = yaml.load(open('config.yaml', 'r'), Loader=yaml.SafeLoader)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = env['upload_path']
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def process_video(video_path):
    def on_detection(start_time, end_time, success):
        print("socket emit")
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

    ShotDetector(video_path, on_detection, on_complete)

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


if __name__ == "__main__":
    socketio.run(app, debug=True)