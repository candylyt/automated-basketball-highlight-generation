# Avi Shah - Basketball Shot Detector/Tracker - July 2023
from PIL import Image
from ultralytics import YOLO
import cv2
import cvzone
import math
import numpy as np
from utils import clean_hoop_pos, clean_ball_pos, detect_score, in_score_region
import os, shutil
import yaml
import datetime
from pathlib import Path
from datetime import timedelta
import time
from enum import Enum

# get environment variables
env = yaml.load(open('config.yaml', 'r'), Loader=yaml.SafeLoader)
print("Environment variables: ", env)

class ShotDetector:
    def __init__(self, video_path, on_detect, on_complete, show_vid=False):
        self.model = YOLO(env['weights_path'], verbose=False)
        self.class_names = env['classes']
        self.colors = [(0, 255, 0), (255, 255, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)]
        self.detect_callback = on_detect
        self.on_complete = on_complete
        self.show_vid = show_vid

        
        self.cap = cv2.VideoCapture(video_path)
        self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)
        print(f"FPS: {self.frame_rate}")

        self.ball_pos = []  # array of tuples ((x_pos, y_pos), frame count, width, height, conf)
        self.hoop_pos = []  # array of tuples ((x_pos, y_pos), frame count, width, height, conf)

        self.frame_count = 0
        self.frame = None

        self.width = int(self.cap.get(3))
        self.height = int(self.cap.get(4))

        print(f"Resolution: {self.width} X {self.height}")

        self.makes = 0
        self.attempts = 0
        self.attempt_cooldown = 0
        self.attempt_time = 0

        # For marking if the ball / rim have been detected in the current frame
        self.ball_detected = False
        self.rim_detected = False

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
            print("Saving results to: ", output_name)
            self.out = cv2.VideoWriter(output_name,  cv2.VideoWriter_fourcc(*'mp4v'), self.frame_rate, (self.output_width, self.output_height))
        
        start_time = time.time()
        self.run()
        
        end_time = time.time()
        duration = end_time - start_time
        minutes = int(duration // 60)
        seconds = int(duration % 60)

        print(f"Total processing time: {minutes:02d}:{seconds:02d}")

    def run(self):
        
        while True:
            ret, self.frame = self.cap.read()

            if not ret:
                print("Processing complete")
                break

            self.timestamp = self.cap.get(cv2.CAP_PROP_POS_MSEC)

            
            # resize to match - force 1280 and 720 for better model results
            det_frame = cv2.resize(self.frame, (1280, 720))

            results = self.model(det_frame, stream=True, verbose=False, imgsz=1280)

            for r in results:

                #TODO: better way to get max conf boxes only
                boxes = sorted([(box.xyxy[0], box.conf, box.cls) for box in r.boxes], key=lambda x: -x[1])
                #sort and get only top prediction for ball / hoop

                # Reset detection variables
                self.ball_detected, self.rim_detected = False, False

                for box in boxes:
                    
                    # Only one ball / rim should be detected per frame
                    if self.ball_detected and self.rim_detected:
                        break
                    
                    # Bounding box
                    x1, y1, x2, y2 = box[0]

                    # Scale back up to original dimensions
                    x1, y1, x2, y2 = int(x1 * self.width/1280), int(y1 * self.height/720), int(x2 * self.width/1280), int(y2* self.height/720)
                    w, h = x2 - x1, y2 - y1

                    # Confidence
                    conf = math.ceil((box[1] * 100)) / 100

                    # Class Name
                    cls = int(box[2])
                    current_class = self.class_names[cls]

                    center = (int(x1 + w / 2), int(y1 + h / 2))

                    if (conf > 0.4 and current_class == 'rim' and not self.rim_detected) or (conf > 0.4 and current_class == 'basketball' and not self.ball_detected):

                        if self.show_vid or self.save or self.screenshot:
                            self.draw_bounding_box(current_class, conf, cls, x1, y1, x2, y2)
                        
                        if current_class == 'rim':
                            self.rim_detected = True
                            self.hoop_pos.append((center, self.frame_count, w, h, conf))
                        elif current_class == 'basketball':
                            self.ball_detected = True
                            self.ball_pos.append((center, self.frame_count, w, h, conf))

            self.clean_motion()
            self.score_detection()
            # self.display_score()
            self.frame_count += 1

            if self.attempt_cooldown > 0:
                self.attempt_cooldown -= 1

            if self.show_vid or self.save or self.screenshot:
                self.draw_overlay()

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
        self.on_complete(self.attempts, self.makes)
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
                        self.makes += 1
                        self.attempts += 1
                        self.detect_callback(max(0, self.timestamp-3000), self.timestamp+2000, True)
                        print(f"[{str(timedelta(milliseconds=self.timestamp)).split('.')[0]}] Shot made")
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
                        self.overlay_color = (0, 0, 255)
                        self.fade_counter = self.fade_frames
                        self.detect_callback(max(0, self.timestamp-3000), self.timestamp+2000, False)
                        print(f"[{str(timedelta(milliseconds=self.timestamp)).split('.')[0]}] Attempt made")
                        self.attempts += 1
                        
                        self.attempt_cooldown = self.MISS_ATTEMPT_COOLDOWN
                        self.screen_shot_moment = True
                        
                    
                    self.attempt_time = 0
                    self.ball_entered = False
                    self.last_point_in_region = None


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


if __name__ == "__main__":
    ShotDetector(env['input'], lambda x,y,z: 0, lambda x, y: print(f"Shot made: {y}\n Attempts: {x}\n Success rate: {y/x*100}%"), False)
    # def __init__(self, video_path, on_detect, on_complete, show_vid=False):




