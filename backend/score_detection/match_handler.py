# match_handler.py

import threading
from shot_detector import ShotDetector
from score_counter import (
    MatchScoreCounter, 
    ScoreCounter
)
from shot_localizer import ShotLocalizer
from utils import get_time_string
import os
import uuid


from logger import (
    INFO,
    SOCKET,
    Logger
)

logger = Logger([
    INFO
])

class MatchHandler:
    def __init__(self, video1_path, video2_path, 
                 quarter_timestamps, is_match=False, is_switched=False, switch_time='99:99:99',
                 points1=None, points2=None, 
                 image_dimensions1=None, image_dimensions2=None,
                 on_detection_callback=None, on_complete_callback=None):
        """
        Initialize the match handler with two videos
        
        Args:
            video1_path: Path to video for team A's basket
            video2_path: Path to video for team B's basket
            quarter_timestamps: List of timestamps for quarters
            is_switched: Whether teams switch sides
            switch_time: When teams switch sides
            points1: Four corner points of penalty box in video1
            points2: Four corner points of penalty box in video2
            image_dimensions1: Dimensions of video1
            image_dimensions2: Dimensions of video2
            on_detection_callback: Callback for shot detection
            on_complete_callback: Callback for completion
        """
        self.video1_path = video1_path
        self.video2_path = video2_path
        
        #TODO: move required parsing of these data members to this class
        self.quarter_timestamps = quarter_timestamps
        self.is_switched = is_switched
        self.switch_time = switch_time
        self.is_match = is_match
        self.run_id = uuid.uuid4()  # Unique ID for this run, can be used for logging or tracking
        
        # Initialize score counter
        self.score_counter = None
        if self.is_match:
            self.score_counter = MatchScoreCounter(quarter_timestamps, is_switched, switch_time)
        else:
            self.score_counter = ScoreCounter(quarter_timestamps)
        
        # Initialize shot localizers if points are provided
        self.localizer1 = None
        self.localizer2 = None
        if points1 and image_dimensions1:
            self.localizer1 = ShotLocalizer(points1, image_dimensions1)
        if is_match and points2 and image_dimensions2:
            self.localizer2 = ShotLocalizer(points2, image_dimensions2)
            
        # Store callbacks from app.py
        self.on_detection_callback = on_detection_callback
        self.on_complete_callback = on_complete_callback
        
        # Initialize processing state
        self.video_1_complete = False
        self.video_2_complete = not self.is_match

        # Initialize shot data 
        self.shot_data_team_A = []
        self.shot_data_team_B = []

        # Thread synchronization
        self.lock = threading.Lock()
        
    def on_shot_detection(self, timestamp, success, video_id, shot_location=None):
        """Callback for shot detection from either detector"""
        mapped_location = (None, None)
        logger.log(INFO, f"Handler callback: timestamp={timestamp}, success={success}, video_id={video_id}, shot_location={shot_location}")
        # Map shot location if available
        if shot_location:
            if video_id == 1 and self.localizer1:
                mapped_location = self.localizer1.map_to_court(shot_location)
            elif video_id == 2 and self.localizer2:
                mapped_location = self.localizer2.map_to_court(shot_location)
        
        logger.log(INFO, f"Mapped location: {mapped_location}")

        
        # Update score counter

        timestring = get_time_string(timestamp)
        with self.lock:
            if success:
                team_id = self.score_counter.make(timestring, video_id)
            else:
                team_id = self.score_counter.attempt(timestring, video_id)

        # Forward to main callback
        start_time = get_time_string(timestamp-3000)
        end_time = get_time_string(timestamp+2000)

        if video_id == 1:
            self.shot_data_team_A.append((timestring, success, team_id, mapped_location[0], mapped_location[1]))
        elif video_id == 2:
            self.shot_data_team_B.append((timestring, success, team_id, mapped_location[0], mapped_location[1]))

        if self.on_detection_callback:
            self.on_detection_callback(start_time, end_time, success, team_id)
    
    def on_team_complete(self, video_id):
        """Callback when either detector completes"""
        with self.lock:
            #TODO: results do not need to be returned, directly get from score counter after both finished
            if video_id == 1:
                self.video_1_complete = True
            elif video_id == 2:
                self.video_2_complete = True
                
            # If both completed, call final callback

            #TODO: implement and call statistic class here
            if self.video_1_complete and self.video_2_complete:
                results = self.score_counter.report()
                for k,v in results.items():
                    logger.log(INFO, f"{k.ljust(16)} : {v}")
                
                # Write shot data
                os.makedirs(f'data/{self.run_id}', exist_ok=True)
                if self.is_match:
                    if self.shot_data_team_A:
                        data_A_path = f'data/{self.run_id}/team_A_shot_data.txt'
                        with open(data_A_path, 'w') as f:
                            for line in self.shot_data_team_A:
                                f.write(','.join(map(str, line))+'\n')
                    
                    if self.shot_data_team_B:
                        data_B_path = f'data/{self.run_id}/team_B_shot_data.txt'
                        with open(data_B_path, 'w') as f:
                            for line in self.shot_data_team_B:
                                f.write(','.join(map(str, line))+'\n')
                
                else:
                    if self.shot_data_team_A:
                        data_A_path = f'data/{self.run_id}/shot_data.txt'
                        with open(data_A_path, 'w') as f:
                            for line in self.shot_data_team_A:
                                f.write(','.join(map(str, line))+'\n')
                
                
                
                if self.on_complete_callback:
                    self.on_complete_callback(results, True)

                
    
    def start_processing(self):
        """Start processing both videos in separate threads"""
        # Start Team A video processing
        thread_a = threading.Thread(
            target=self._process_video,
            args=(self.video1_path, 1)
        )
        
        thread_a.daemon = True
        
        thread_b = None
        if self.is_match:
        # Start Team B video processing
            thread_b = threading.Thread(
                target=self._process_video, 
                args=(self.video2_path, 2)
            )
        
            thread_b.daemon = True
        
        thread_a.start()
        
        if thread_b:
            thread_b.start()
        
        return "Processing started"
    
    # Entry point of video processing
    def _process_video(self, video_path, video_id):
        """Process a single video for the specified team"""
        def on_detection(timestamp, success, _video_id, shot_location=None):
            # Here we intercept the detection and associate it with the team
            self.on_shot_detection(timestamp, success, _video_id, shot_location)
            
        def on_complete():
            # Process completion for this team
            self.on_team_complete(video_id)
        
        # Create and run detector
        # Note: We need to modify ShotDetector to accept video_id parameter
        # and return shot_location when it detects a shot
        ShotDetector(
            video_path, 
            on_detection, 
            on_complete, 
            show_vid=False,
            video_id=video_id,  # New parameter to identify the team
            score_counter=self.score_counter  # Pass the shared score counter
        )