# TODO: Review changes needed here
from PIL import Image
from ultralytics import YOLO
import cv2
import cvzone
import math
import numpy as np
import os, shutil
import yaml
import datetime
from pathlib import Path
from datetime import timedelta, datetime
import time
from enum import Enum
import threading
from queue import Queue, Empty
from copy import deepcopy

from utils import (
    clean_hoop_pos, 
    clean_ball_pos, 
    detect_score, 
    in_score_region,
    get_time_string
)

from score_counter import (
    ScoreCounter,
    MatchScoreCounter
)

from logger import (
    INFO,
    SOCKET,
    Logger
)

# get environment variables
env = yaml.load(open('config.yaml', 'r'), Loader=yaml.SafeLoader)
print("Environment variables: ", env)

logger = Logger([
    INFO
])

class ShotDetector:
    def __init__(self, 
                video_path,             # Video path for processing
                on_detect,              # on_detect(timestamp, success, team_id, shot_location) -> Callback to MatchHandler for when a shot is detected
                on_complete,            # on_complete(team_id) -> Callback to MatchHandler for when video finishes processing
                show_vid=False,         # Show CV2 window while processing, for debugging, will significantly slow down program
                video_id=None,           # 1 or 2
                **kwargs):
        
        #TODO: initialize with team_id, updated based on switch timestamp
        self.model = YOLO(env['weights_path'], verbose=False)
        self.model_shoot = YOLO(env['weights_path_shoot'], verbose=False)
        self.class_names = env['classes']
        self.class_names_shoot = env['classes_shoot']
        self.colors = [(0, 255, 0), (255, 255, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)]
        self.colors_shoot = [(0, 255, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)]
        self.on_detect = on_detect
        self.on_complete = on_complete
        self.show_vid = show_vid

        # for debug
        self.video_name = video_path.split("/")[-1].replace(".mp4", "")
        self.output_true_shot = f"true_shot_frames_{self.video_name}"
        self.output_all_shot = f"all_shot_frames_{self.video_name}"
        os.makedirs(self.output_true_shot, exist_ok=True)
        os.makedirs(self.output_all_shot, exist_ok=True)
        
        self.cap = cv2.VideoCapture(video_path)
        self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
        logger.log(INFO, f"FPS: {self.frame_rate}")

        self.ball_pos = []  # array of tuples ((x_pos, y_pos), frame count, width, height, conf)
        self.hoop_pos = []  # array of tuples ((x_pos, y_pos), frame count, width, height, conf)
        self.frame_track = [] # array of tuples (det_frame, timestamp)
        self.num_frames_to_track = 2 * self.frame_rate # 2 seconds before
        self.frame_count = 0
        self.frame = None

        self.width = int(self.cap.get(3))
        self.height = int(self.cap.get(4))

        logger.log(INFO, f"Resolution: {self.width} X {self.height}")

        self.makes = 0
        self.attempts = 0
        self.attempt_cooldown = 0
        self.attempt_time = 0

        # Not needed, these will be handled in MatchHandler

        self.video_id = video_id
        #TODO: modify init of data members
        # self.is_match = kwargs.get('is_match', False)
        # quarters = kwargs.get('quarter_timestamps', [])
        # quarters = [i for i in quarters if i != '']
        # is_switched = kwargs.get('is_switched', False)
        # switch_time = kwargs.get('switch_time', '99:99:99')
        
        # TODO: modify scorecounter init
        # if not self.is_match:
        #     self.score_counter = ScoreCounter(quarters)
        # else:
        #     self.score_counter = MatchScoreCounter(quarters, is_switched, switch_time)

        # For marking if the ball / rim have been detected in the current frame
        self.ball_detected = False
        self.rim_detected = False
        self.should_detect_shot = False
        # Used for green and red colors after make/miss
        self.fade_frames = 20
        self.fade_counter = 0
        self.overlay_color = (0, 0, 0)
        self.last_point_in_region = None
        
        self.screen_shot_count = 0
        self.screenshot = env['screenshot']
        self.screen_shot_moment = False
        self.screen_shot_path = env['screenshot_path']
        self.save = env['save_video']
        Path(self.screen_shot_path).mkdir(parents=True, exist_ok=True)



        self.attempt_cooldown = 0
        self.timestamp = None
        self.ball_entered = False

        self.MISS_ATTEMPT_COOLDOWN = int(self.frame_rate * 2.5)
        self.MADE_ATTEMPT_COOLDOWN = int(self.frame_rate * 3)
        self.ATTEMPT_DETECTION_INTERVAL = int(self.frame_rate * 0.3)

        self.output_width = env['output_width']
        self.output_height = env['output_height']

        if self.save:
            output_name = env['output_path'] + '/' + env['input'].split("/")[-1].split('.')[0] + str(datetime.datetime.now()) 
            output_name = output_name.replace(':','-').replace('.','-') + ".mp4"
            logger.log(INFO, "Saving results to: ", output_name)
            self.out = cv2.VideoWriter(output_name,  cv2.VideoWriter_fourcc(*'mp4v'), self.frame_rate, (self.output_width, self.output_height))
        
        # Threading components
        self.detection_queue = Queue()
        self.detection_thread = None
        self.detection_thread_active = True
        self.detection_lock = threading.Lock()
        
        # Start detection worker thread
        self.detection_thread = threading.Thread(target=self._detection_worker)
        self.detection_thread.daemon = True
        self.detection_thread.start()

        start_time = time.time()
        self.run()
        
        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        logger.log(INFO, f"Total processing time: {minutes:02d}:{seconds:02d}")

    def run(self):
        while True:
            ret, self.frame = self.cap.read()

            if not ret:
                logger.log(INFO, "Processing complete")
                # Signal detection thread to stop
                self.detection_thread_active = False
                break

            self.timestamp = self.cap.get(cv2.CAP_PROP_POS_MSEC)

            # resize to match - force 1280 and 720 for better model results
            det_frame = cv2.resize(self.frame, (1280, 720))

            results = self.model_shoot(det_frame, stream=True, verbose=False, imgsz=1280)

            for r in results:
                #TODO: better way to get max conf boxes only
                boxes = sorted([(box.xyxy[0], box.conf, box.cls) for box in r.boxes], key=lambda x: -x[1])
                #sort and get only top prediction for ball / hoop
                has_shoot = False
                # Reset detection variables
                self.ball_detected, self.rim_detected = False, False

                # Define confidence thresholds for each class
                conf_thresholds = {
                    'rim': 0.4,
                    'basketball': 0.4,
                    'shoot': 0.5,
                    'person': 0.35
                }

                # Store bounding box info for each class
                frame_boxes = {
                    'rim': None,
                    'basketball': None,
                    'shoot': None,
                    'person': []
                }

                for box in boxes:
                    # Bounding box
                    x1, y1, x2, y2 = box[0]

                    # Scale back up to original dimensions
                    x1, y1, x2, y2 = int(x1 * self.width/1280), int(y1 * self.height/720), int(x2 * self.width/1280), int(y2* self.height/720)
                    w, h = x2 - x1, y2 - y1

                    # Confidence
                    conf = math.ceil((box[1] * 100)) / 100

                    # Class Name
                    cls = int(box[2])
                    # print(f"cls: {cls}")
                    current_class = self.class_names[cls]

                    center = (int(x1 + w / 2), int(y1 + h / 2))

                    # Store box info based on class and confidence threshold
                    if current_class in conf_thresholds and conf > conf_thresholds[current_class]:
                        box_info = {
                            'center': center,
                            'width': w,
                            'height': h,
                            'confidence': conf,
                            'coords': (x1, y1, x2, y2)
                        }

                        if current_class == 'rim' and not frame_boxes['rim']:
                            frame_boxes['rim'] = box_info
                            self.rim_detected = True
                            self.hoop_pos.append((center, self.frame_count, w, h, conf))
                        elif current_class == 'basketball' and not frame_boxes['basketball']:
                            frame_boxes['basketball'] = box_info
                            self.ball_detected = True
                            self.ball_pos.append((center, self.frame_count, w, h, conf))
                        elif current_class == 'shoot' and not frame_boxes['shoot']:
                            frame_boxes['shoot'] = box_info
                            has_shoot = True
                            
                        elif current_class == 'person':
                            frame_boxes['person'].append(box_info)
                    if has_shoot:
                        # Save annotated frame as image if shoot detected
                        annotated_frame = r.plot()
                        frame_filename = os.path.join(self.output_all_shot, f"all_shot_{self.frame_count}_{get_time_string(self.timestamp)}.jpg")
                        
                        cv2.imwrite(frame_filename, annotated_frame)
            
            # Store frame boxes info instead of frame
            # TODO: do not need to add frame_boxes
            if len(self.frame_track) >= self.num_frames_to_track:
                self.frame_track.pop(0)
            self.frame_track.append((frame_boxes,self.frame_count, self.timestamp, self.frame))

            self.clean_motion()
            self.score_detection()

            

            self.frame_count += 1

            if self.attempt_cooldown > 0:
                self.attempt_cooldown -= 1

            if self.show_vid or self.save or self.screenshot:
                # self.draw_overlay()
                # self.draw_overlay()

                if self.show_vid:
                    cv2.imshow('Frame', self.frame)
                    # Close if 'q' is clicked
                    if cv2.waitKey(1) & 0xFF == ord('q'):  # higher waitKey slows video down, use 1 for webcam
                        break

                if self.screen_shot_moment:
                    cv2.imwrite(f"{self.screen_shot_path}/{self.screen_shot_count}.png", self.frame)
                    self.screen_shot_moment = False
                    self.screen_shot_count += 1

                if self.save:
                    self.out.write(cv2.resize(self.frame, (env['output_width'], env['output_height'])))

        # Report score and cleanup upon finish
        # score_report = self.score_counter.report()
        # for k,v in score_report.items():
        #     logger.log(INFO, f"{k.ljust(16)} : {v}")
        
        # self.on_complete(score_report, self.is_match)
        
        # Wait for detection thread to finish
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join(timeout=5.0)
            
        self.on_complete()
        
        self.cap.release()
        if self.show_vid:
            cv2.destroyAllWindows()

    # Function to draw bounding box for ball and rim
    def draw_bounding_box(self, current_class, conf, cls, x1, y1, x2, y2):
                        
        label = f"{current_class}: {conf}"
        color = self.colors[cls]

        self.frame = cv2.rectangle(self.frame, (x1, y1), (x2, y2), color, 2)

        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        self.frame = cv2.rectangle(self.frame, (x1, y1 - 20), (x1 + text_w, y1), color, -1)
        self.frame = cv2.putText(self.frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Function to draw overlay elements, mainly for debugging purposes
    def draw_overlay(self):
        if self.hoop_pos and self.rim_detected:
            # draw score-region
            x1 = self.hoop_pos[-1][0][0] - 2  * self.hoop_pos[-1][2]
            x2 = self.hoop_pos[-1][0][0] + 2  * self.hoop_pos[-1][2]
            y1 = self.hoop_pos[-1][0][1] - 3.5  * self.hoop_pos[-1][3]
            y2 = self.hoop_pos[-1][0][1] + 0.9 * self.hoop_pos[-1][3]

            pts = np.array([[x1, y1], [x2,y1], [x2, y2], [x1, y2]], np.int32)

            pts = pts.reshape((-1, 1, 2))

            self.frame = cv2.polylines(self.frame, [pts], True, (255, 0, 255), 3)

            #draw hoop-line
            hoop_y = self.hoop_pos[-1][0][1]
            x1 = self.hoop_pos[-1][0][0] - 0.5 * self.hoop_pos[-1][2]
            x2 = self.hoop_pos[-1][0][0] + 0.5 * self.hoop_pos[-1][2]

            pts = np.array([[x1, hoop_y], [x2, hoop_y]], np.int32)

            pts = pts.reshape((-1, 1, 2))

            self.frame = cv2.polylines(self.frame, [pts], True, (0, 255, 255), 2)

        #draw timestamp
        timestring = str(timedelta(milliseconds=self.timestamp)).split('.')[0]
        cv2.putText(self.frame, timestring, (int(self.width*0.9), 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        cv2.putText(self.frame, timestring, (int(self.width*0.9), 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 4)

        #display ball trajectory
        for i in range(0, len(self.ball_pos)):
            color = (0, 0, 255) if i == len(self.ball_pos)-1 else (100, 100, 100, 0.5)
            thickness = 5 if i == len(self.ball_pos)-1 else 2
                
            cv2.circle(self.frame, self.ball_pos[i][0], 2, color, thickness)

        #draw lines between ball positions in consecutive frames
        if len(self.ball_pos) > 1 and self.ball_detected:
            if self.last_point_in_region:
                x1, x2 = self.ball_pos[-1][0][0], self.ball_pos[-1][0][1]
                y1, y2 = self.last_point_in_region[0][0], self.last_point_in_region[0][1]

                pts = np.array([[x1, x2], [y1, y2]], np.int32)
        
                pts = pts.reshape((-1, 1, 2))

                cv2.polylines(self.frame, [pts], True, (0, 0, 255), 2)

        self.display_score()


    # Function to clean likely erroneous detections
    def clean_motion(self):
        # Clean and display ball motion
        self.ball_pos = clean_ball_pos(self.ball_pos, self.frame_count)
        
        # Clean hoop motion and display current hoop center
        if len(self.hoop_pos) > 1:
            self.hoop_pos = clean_hoop_pos(self.hoop_pos)

    # Function to handle scoring moment detection logic
    def score_detection(self):
        #only execute if hoop and ball pos is known
        if len(self.hoop_pos) > 0 and len(self.ball_pos) > 0:
            
            # Made: Enters hoop region, shortly after enters down region, 
            # Attempt: Enters up region, then exits up region without entering hoop region
            if self.ball_detected and self.attempt_cooldown == 0:
                if in_score_region(self.ball_pos, self.hoop_pos):
                    if self.ball_entered:
                        self.attempt_time += 1
                    else:
                        self.ball_entered = True
                        self.attempt_time = 1
                    

                    #Add linear interpolation
                    if not self.last_point_in_region:
                        self.last_point_in_region = self.ball_pos[-1]
                        scored = False
                    else: 
                        scored = detect_score(self.ball_pos, self.hoop_pos, self.last_point_in_region)

                    # self.attempts += 1
                    # self.frame = cv2.putText(self.frame, 'DOWN', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    if scored:
                        # print(self.ball_pos[-1], self.last_point_in_region, self.hoop_pos[-1])
                        # time_string = get_time_string(self.timestamp)
                        self.makes += 1
                        self.attempts += 1
                        
                        # Create detection task dictionary with current state
                        detection_task = {
                            'frame_track': deepcopy(self.frame_track),
                            'timestamp': self.timestamp,
                            'is_scored': True,
                            'video_id': self.video_id
                        }
                        self.detection_queue.put(detection_task)
                        
                        # shot_location, shot_timestamp = self.shot_detection()
                        
                        # if shot_location:
                        #     scaled_shot_location = (shot_location[0] / self.width, shot_location[1] / self.height)
                        # else:
                        #     scaled_shot_location = (None, None)
                        
                        # if shot_timestamp:
                        #     logger.log(INFO, f"Shot detected at {shot_timestamp}  |  Location: {shot_location}")
                        # self.on_detect(self.timestamp, True, self.video_id, scaled_shot_location)
                        # move shoot detection here
                        # self.should_detect_shot = True

                        # logger.log(INFO, f"[{time_string}] {'Shot made'.ljust(13)} | Side {side} | Team {team}")
                    # else:
                    #     self.detect_callback(max(0, self.timestamp-3000), self.timestamp+2000, False)
                    #     print("attempt made")
                        self.overlay_color = (0, 255, 0)
                        self.fade_counter = self.fade_frames
                        self.attempt_cooldown = self.MADE_ATTEMPT_COOLDOWN
                        self.screen_shot_moment = True
                        self.last_point_in_region = None
                        self.ball_entered = False
                        self.attempt_time = 0
                    
                    else:
                        self.last_point_in_region = self.ball_pos[-1]
                

                else:
                    if self.attempt_time >= self.ATTEMPT_DETECTION_INTERVAL:
                        time_string = get_time_string(self.timestamp)
                        self.overlay_color = (0, 0, 255)
                        self.fade_counter = self.fade_frames

                        # Create detection task dictionary with current state
                        detection_task = {
                            'frame_track': deepcopy(self.frame_track),
                            'timestamp': self.timestamp,
                            'is_scored': False,
                            'video_id': self.video_id
                        }
                        self.detection_queue.put(detection_task)

                        # on_detect(timestamp, success, video_id, shot_location)
                        # shot_location, shot_timestamp = self.shot_detection()
                        # if shot_location:
                        #     scaled_shot_location = (shot_location[0] / self.width, shot_location[1] / self.height)
                        # else:
                        #     scaled_shot_location = (None, None)
                        
                        # if shot_timestamp:
                        #     #TODO: logic for shot localization
                        #     logger.log(INFO, f"Shot detected at {shot_timestamp}  |  Location: {shot_location}")

                        # self.on_detect(self.timestamp, False, self.video_id, scaled_shot_location)
                        # move shoot detection here
                        # self.should_detect_shot = True
                        # logger.log(INFO, f"[{time_string}] {'Attempt made'.ljust(13)} | Side {side} | Team {team}")
                        self.attempts += 1
                        
                        self.attempt_cooldown = self.MISS_ATTEMPT_COOLDOWN
                        self.screen_shot_moment = True
                        
                    
                    self.attempt_time = 0
                    self.ball_entered = False
                    self.last_point_in_region = None
    # def shot_detection(self):
    #     """
    #     Detect shooting motion in previous frames and identify the exact shooting moment.
    #     Returns the timestamp of the shooting moment if found, None otherwise.
    #     """
    #     shot_location = None
    #     shooter_positions = []
    #     debug_timestamp = None
    #     debug_frame = None
    #     debug_frame_count = None
    #     # Step 1: Find frames with "shoot" class
    #     for frame_data in self.frame_track:
    #         frame_boxes, frame_count, timestamp, frame_img = frame_data
    #         logger.log(INFO, f"Frame {frame_count} at {get_time_string(timestamp)}")
    #         if frame_boxes['shoot']:
    #             shoot_box = frame_boxes['shoot']  # Only one shoot box                
    #             # Step 2: Find nearest person to the shoot box by calculating overlap
    #             if frame_boxes['person']:
    #                 person_boxes = frame_boxes['person']
                    
    #                 max_overlap = 0
    #                 closest_person = None
                    
    #                 # Get shoot box coordinates (y increases downward)
    #                 x1_shoot = shoot_box['coords'][0]  # Left
    #                 y1_shoot = shoot_box['coords'][1]  # Top
    #                 x2_shoot = shoot_box['coords'][2]  # Right 
    #                 y2_shoot = shoot_box['coords'][3]  # Bottom
                    
    #                 for person_box in person_boxes:
    #                     # Get person box coordinates (y increases downward)
    #                     x1_person = person_box['coords'][0]  # Left
    #                     y1_person = person_box['coords'][1]  # Top
    #                     x2_person = person_box['coords'][2]  # Right
    #                     y2_person = person_box['coords'][3]  # Bottom
                        
    #                     # Calculate intersection
    #                     # x_left is the rightmost of the left edges
    #                     x_left = max(x1_shoot, x1_person)
    #                     # y_top is the bottommost of the top edges
    #                     y_top = max(y1_shoot, y1_person)
    #                     # x_right is the leftmost of the right edges
    #                     x_right = min(x2_shoot, x2_person)
    #                     # y_bottom is the topmost of the bottom edges
    #                     y_bottom = min(y2_shoot, y2_person)
                        
    #                     if x_right > x_left and y_bottom > y_top:
    #                         overlap_area = (x_right - x_left) * (y_bottom - y_top)
    #                         if overlap_area > max_overlap:
    #                             max_overlap = overlap_area
    #                             closest_person = person_box
                    
    #                 # Calculate shoot box area
    #                 shoot_box_area = (x2_shoot - x1_shoot) * (y2_shoot - y1_shoot)
    #                 if closest_person and max_overlap >= 0.7 * shoot_box_area:
    #                     # shooting_moments.append((timestamp, timestamp))
    #                     # record the person's bottom-center position in the frame
    #                     x1, y1, x2, y2 = closest_person['coords']
    #                     bottom_center_x = x1 + (x2 - x1) // 2  # Center x coordinate
    #                     bottom_center_y = y2  # Bottom y coordinate
    #                     shooter_positions.append((bottom_center_x, bottom_center_y))
    #                     if not debug_timestamp:
    #                         debug_timestamp = get_time_string(timestamp)
    #                         debug_frame = frame_img
    #                         debug_frame_count = frame_count

    #     # Step 3: Use IQR to filter outliers
    #     # By collecting all the possible shooting positions, we calculate the average position of "the shooter"
    #     # remove outlier to avoid false positive
    #     if shooter_positions:
    #         x_coords = [pos[0] for pos in shooter_positions]
    #         y_coords = [pos[1] for pos in shooter_positions]
            
    #         # Calculate Q1, Q3 and IQR for both x and y coordinates
    #         q1_x, q3_x = np.percentile(x_coords, [25, 75])
    #         q1_y, q3_y = np.percentile(y_coords, [25, 75])
    #         iqr_x = q3_x - q1_x
    #         iqr_y = q3_y - q1_y
            
    #         # Define bounds
    #         x_lower = q1_x - 1.5 * iqr_x
    #         x_upper = q3_x + 1.5 * iqr_x
    #         y_lower = q1_y - 1.5 * iqr_y
    #         y_upper = q3_y + 1.5 * iqr_y
            
    #         # Filter out outliers
    #         filtered_positions = [
    #             pos for pos in shooter_positions 
    #             if (x_lower <= pos[0] <= x_upper and y_lower <= pos[1] <= y_upper)
    #         ]
            
    #         if filtered_positions:
    #             # Calculate average position
    #             avg_x = sum(pos[0] for pos in filtered_positions) / len(filtered_positions)
    #             avg_y = sum(pos[1] for pos in filtered_positions) / len(filtered_positions)
    #             shot_location = (avg_x, avg_y)
        
    #         # Plot shot location on debug frame if available
    #         if debug_frame is not None and shot_location is not None:
    #             # Convert coordinates to integers for cv2
    #             plot_x = int(avg_x)
    #             plot_y = int(avg_y)
                
    #             # Draw red circle at shot location
    #             cv2.circle(debug_frame, (plot_x, plot_y), 5, (0,0,255), -1)
                
    #             # Save the annotated frame
    #             output_path = os.path.join(self.output_true_shot, f"true_shot_{debug_frame_count}_{debug_timestamp}.jpg")
    #             cv2.imwrite(output_path, debug_frame)
    #         return shot_location, debug_timestamp

    #     return None, None
                

    def display_score(self):
        # Add text
        text = str(self.makes) + " / " + str(self.attempts)
        cv2.putText(self.frame, text, (50, 125), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 6)
        cv2.putText(self.frame, text, (50, 125), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 3)
        cv2.putText(self.frame, str(self.attempt_time), (50, 250), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

        # Gradually fade out color after shot
        if self.fade_counter > 0:
            alpha = 0.2 * (self.fade_counter / self.fade_frames)
            self.frame = cv2.addWeighted(self.frame, 1 - alpha, np.full_like(self.frame, self.overlay_color), alpha, 0)
            self.fade_counter -= 1

    def get_side(self):
        if len(self.hoop_pos):
            return 1 if self.hoop_pos[-1][0][0] > self.width/2 else 0

        return None
    
    def _detection_worker(self):
        """Background thread that processes shot detection tasks."""
        while self.detection_thread_active:
            try:
                # Get detection task dictionary from queue
                task = self.detection_queue.get(timeout=1.0)
                
                # Process the detection
                shot_location, shot_timestamp = self._process_shot_detection(task['frame_track'])
                
                # Scale shot location if found
                if shot_location:
                    scaled_shot_location = (shot_location[0] / self.width, shot_location[1] / self.height)
                else:
                    scaled_shot_location = (None, None)
                
                # Log detection results using preserved state
                logger.log(INFO, f"Score detected at {get_time_string(task['timestamp'])} | "
                            f"Location: {scaled_shot_location} | "
                            f"Video: {task['video_id']} | "
                            f"{'Made' if task['is_scored'] else 'Missed'}")

                # Call on_detect with preserved state
                self.on_detect(task['timestamp'], task['is_scored'], task['video_id'], scaled_shot_location)

            except Empty:
                # Queue timeout - continue waiting
                continue
            except Exception as e:
                logger.log(INFO, f"Error in detection worker: {str(e)}")
                continue

    def _process_shot_detection(self, frame_track):
        """
        Process shot detection on a snapshot of frame_track.
        This is the same as the original shot_detection method but works on passed data.
        """
        shot_location = None
        shooter_positions = []
        debug_timestamp = None
        debug_frame = None
        debug_frame_count = None
        
        # Step 1: Find frames with "shoot" class
        for frame_data in frame_track:
            frame_boxes, frame_count, timestamp, frame_img = frame_data
            if frame_boxes['shoot']:
                shoot_box = frame_boxes['shoot']  # Only one shoot box                
                # Step 2: Find nearest person to the shoot box by calculating overlap
                if frame_boxes['person']:
                    person_boxes = frame_boxes['person']
                    
                    max_overlap = 0
                    closest_person = None
                    
                    # Get shoot box coordinates (y increases downward)
                    x1_shoot = shoot_box['coords'][0]  # Left
                    y1_shoot = shoot_box['coords'][1]  # Top
                    x2_shoot = shoot_box['coords'][2]  # Right 
                    y2_shoot = shoot_box['coords'][3]  # Bottom
                    
                    for person_box in person_boxes:
                        # Get person box coordinates (y increases downward)
                        x1_person = person_box['coords'][0]  # Left
                        y1_person = person_box['coords'][1]  # Top
                        x2_person = person_box['coords'][2]  # Right
                        y2_person = person_box['coords'][3]  # Bottom
                        
                        # Calculate intersection
                        x_left = max(x1_shoot, x1_person)
                        y_top = max(y1_shoot, y1_person)
                        x_right = min(x2_shoot, x2_person)
                        y_bottom = min(y2_shoot, y2_person)
                        
                        if x_right > x_left and y_bottom > y_top:
                            overlap_area = (x_right - x_left) * (y_bottom - y_top)
                            if overlap_area > max_overlap:
                                max_overlap = overlap_area
                                closest_person = person_box
                    
                    # Calculate shoot box area
                    shoot_box_area = (x2_shoot - x1_shoot) * (y2_shoot - y1_shoot)
                    if closest_person and max_overlap >= 0.7 * shoot_box_area:
                        x1, y1, x2, y2 = closest_person['coords']
                        bottom_center_x = x1 + (x2 - x1) // 2  # Center x coordinate
                        bottom_center_y = y2  # Bottom y coordinate
                        shooter_positions.append((bottom_center_x, bottom_center_y))
                        if not debug_timestamp:
                            debug_timestamp = get_time_string(timestamp)
                            debug_frame = frame_img
                            debug_frame_count = frame_count

        # Step 3: Use IQR to filter outliers
        if shooter_positions:
            x_coords = [pos[0] for pos in shooter_positions]
            y_coords = [pos[1] for pos in shooter_positions]
            
            # Calculate Q1, Q3 and IQR for both x and y coordinates
            q1_x, q3_x = np.percentile(x_coords, [25, 75])
            q1_y, q3_y = np.percentile(y_coords, [25, 75])
            iqr_x = q3_x - q1_x
            iqr_y = q3_y - q1_y
            
            # Define bounds
            x_lower = q1_x - 1.5 * iqr_x
            x_upper = q3_x + 1.5 * iqr_x
            y_lower = q1_y - 1.5 * iqr_y
            y_upper = q3_y + 1.5 * iqr_y
            
            # Filter out outliers
            filtered_positions = [
                pos for pos in shooter_positions 
                if (x_lower <= pos[0] <= x_upper and y_lower <= pos[1] <= y_upper)
            ]
            
            if filtered_positions:
                # Calculate average position
                avg_x = sum(pos[0] for pos in filtered_positions) / len(filtered_positions)
                avg_y = sum(pos[1] for pos in filtered_positions) / len(filtered_positions)
                shot_location = (avg_x, avg_y)
        
            # Plot shot location on debug frame if available
            if debug_frame is not None and shot_location is not None:
                # Convert coordinates to integers for cv2
                plot_x = int(avg_x)
                plot_y = int(avg_y)
                
                # Draw red circle at shot location
                cv2.circle(debug_frame, (plot_x, plot_y), 5, (0,0,255), -1)
                
                # Save the annotated frame
                output_path = os.path.join(self.output_true_shot, f"true_shot_{debug_frame_count}_{debug_timestamp}.jpg")
                cv2.imwrite(output_path, debug_frame)

        return shot_location, debug_timestamp

def get_time_string(timestamp):
    timestamp = max(0, timestamp)



if __name__ == "__main__":
    def print_stats(score_report, is_match):
        makes = len(score_report.get('makes', []))
        attempts = len(score_report.get('attempts', []))
        success_rate = (makes / attempts * 100) if attempts > 0 else 0
        print(f"Shot made: {makes}")
        print(f"Attempts: {attempts}")
        print(f"Success rate: {success_rate:.2f}%")

    ShotDetector(env['input'], lambda x,y,z,k: 0, print_stats, False)




