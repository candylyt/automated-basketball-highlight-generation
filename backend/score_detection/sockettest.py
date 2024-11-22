# test_websocket.py
import socketio
import requests
import time

def test_upload_and_socket():
    # Initialize Socket.IO client
    sio = socketio.Client()
    
    # Socket event handlers
    @sio.on('connect')
    def on_connect():
        print('Connected to server')

    @sio.on('shooting_detected')
    def on_shooting_detected(data):
        print(f"[shooting_detected] Response: {data['start_time']}, {data['end_time']}, {data['success']}")

    @sio.on('processing_complete')
    def on_processing_complete(data):
        print(f"[processing_complete] Response: {data['makes']}/{data['attempts']}")

    # Connect to server
    try:
        sio.connect('http://127.0.0.1:5000')
        
        # Upload video
        files = {'video': open('videos/amateur2.mp4', 'rb')}
        response = requests.post('http://127.0.0.1:5000/upload', files=files)
        print(f"Upload response: {response.json()}")
        
        # Keep connection alive to receive events
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Test ended by user")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sio.disconnect()

if __name__ == "__main__":
    test_upload_and_socket()