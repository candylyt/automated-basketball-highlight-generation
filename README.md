# 🏀 HoopIQ: Real-Time Basketball Analytics & Highlight Generator 🎥
#### Welcome to HoopIQ, your personal basketball analyst and highlight reel wizard! Whether you're an amateur baller looking to up your game or a content creator who wants to turn game footage into jaw-dropping highlights in record time, HoopIQ has got your back. No more waiting for professional analysts or spending hours editing—HoopIQ brings the pros to your pocket!

## 🚀 What is HoopIQ?
HoopIQ is a real-time basketball analytics tool that identifies scoring moments, shooting attempts, and other key events during a game. It automatically generates statistics and highlight reels so you can focus on what really matters: balling out and improving your game.

### Key Features:
* **Real-Time Analytics**: Get instant feedback on your performance, including shooting accuracy, scoring patterns, and more.
* **Automatic Highlight Generation**: Say goodbye to manual editing! HoopIQ creates highlight reels in seconds.
* **Amateur-Friendly**: Designed for players who don't have access to professional analytics teams.
* **Time-Saving**: Cuts down hours of video editing into a few clicks.

## 🎯 Why HoopIQ?
* For Players: Improve your in-game performance with actionable insights. Know your strengths, weaknesses, and areas to focus on.
* For Content Creators: Create highlight reels faster than a Steph Curry three-pointer. Share your best moments with the world in no time.
* For Coaches: Analyze your team's performance without breaking a sweat. HoopIQ does the heavy lifting for you.

## 🛠️ How It Works
1. Record Your Game: Use any camera to record your basketball game.
2. Upload to HoopIQ: Feed the video into HoopIQ.
3. Let the Magic Happen: HoopIQ analyzes the footage, identifies key moments, and generates stats + highlights.
4. Improve & Share: Review your performance, share your highlights, and dominate the court.

## 🤝 Contributing
We're always looking for ballers who can help us improve HoopIQ! Whether you're a developer, designer, or basketball enthusiast, your contributions are welcome.

## 📜 License
HoopIQ is licensed under the MIT License. See [LICENSE](https://github.com/candylyt/automated-basketball-highlight-generation/blob/main/LICENSE) for more details.

# Basketball Shot Analysis Pipeline

This project implements a video analysis pipeline for basketball shot detection and contest analysis. The system processes uploaded videos to detect shots, analyze makes/misses, and determine if shots were contested.

## Features

- Shot detection with make/miss classification
- Video composition of made and missed shots
- Contest analysis for each shot
- Annotated video output
- RESTful API endpoints

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Create necessary directories:
```bash
mkdir -p backend/uploads backend/results
```

3. Start the backend server:
```bash
cd backend
python api.py
```

## API Endpoints

### Upload Video
- **URL**: `/upload`
- **Method**: `POST`
- **Content-Type**: `multipart/form-data`
- **Parameters**:
  - `file`: Video file to analyze
- **Response**:
```json
{
    "status": "success",
    "data": {
        "attempts": 10,
        "makes": 6,
        "made_contested": 3,
        "made_uncontested": 3,
        "missed_contested": 2,
        "missed_uncontested": 2,
        "made_shots_video": "/path/to/made_shots.mp4",
        "missed_shots_video": "/path/to/missed_shots.mp4"
    }
}
```

### Get Video
- **URL**: `/video/{video_type}/{timestamp}`
- **Method**: `GET`
- **Parameters**:
  - `video_type`: Either "made" or "missed"
  - `timestamp`: Analysis timestamp
- **Response**: Video file stream

## Project Structure

```
backend/
├── api.py                  # FastAPI application
├── contest.py             # Contest analysis implementation
├── requirements.txt       # Python dependencies
├── score_detection/      # Shot detection implementation
│   └── shot_detector.py
├── uploads/             # Temporary storage for uploaded videos
└── results/            # Analysis results and composed videos
```

## Implementation Details

1. **Shot Detection**: Uses YOLO model to detect basketball, rim, and shooter positions. Tracks ball trajectory to identify shots and their outcomes.

2. **Video Composition**: Creates separate videos for made and missed shots by extracting relevant segments from the original video.

3. **Contest Analysis**: Analyzes player positions relative to the shooter to determine if shots were contested.

## Notes

- The system requires sufficient GPU memory for YOLO model inference
- Video processing may take some time depending on the length of the input video
- Temporary files are automatically cleaned up after processing
