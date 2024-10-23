# Avi Shah - Basketball Shot Detector/Tracker - July 2023

from ultralytics import YOLO
import cv2
import cvzone
import math
import numpy as np
from utils import score, detect_down, detect_up, in_hoop_region, clean_hoop_pos, clean_ball_pos
import os, shutil
import yaml

env = yaml.load(open('config.yaml', 'r'), Loader=yaml.SafeLoader)
print(env)

class ShotDetector:
    def __init__(self):
        # Load the YOLO model created from main.py - change text to your relative path
        self.model = YOLO(env['WEIGHTS_PATH'])
        self.class_names = env['MODEL_CLASSES']
        self.colors = [(0, 255, 0), (255, 255, 0), (255, 255, 255), (255, 0, 0), (0, 0, 255)]


        # Uncomment line below to use webcam (I streamed to my iPhone using Iriun Webcam)
        # self.cap = cv2.VideoCapture(0)

        # Use video - replace text with your video path
        self.cap = cv2.VideoCapture(env['INPUT'])

        self.ball_pos = []  # array of tuples ((x_pos, y_pos), frame count, width, height, conf)
        self.hoop_pos = []  # array of tuples ((x_pos, y_pos), frame count, width, height, conf)

        self.frame_count = 0
        self.frame = None

        self.width = self.cap.get(3)
        self.height = self.cap.get(4)

        self.makes = 0
        self.attempts = 0

        # Used to detect shots (upper and lower region)
        self.up = False
        self.down = False
        self.up_frame = 0
        self.down_frame = 0

        # Used for green and red colors after make/miss
        self.fade_frames = 20
        self.fade_counter = 0
        self.overlay_color = (0, 0, 0)
        
        self.screen_shot_count = 0
        self.screen_shot = False

        self.run()

    def run(self):
        
        while True:
            ret, self.frame = self.cap.read()

            
            # resize to match 
            det_frame = cv2.resize(self.frame, (640, 640))


            if not ret:
                # End of the video or an error occurred
                break

            results = self.model(det_frame, stream=False, verbose=False)

            for r in results:

                #TODO: better way to get max conf boxes only
                boxes = sorted([(box.xyxy[0], box.conf, box.cls) for box in r.boxes], key=lambda x: -x[1])
                #sort and get only top prediction for ball / hoop

                ball, rim = False, False

                for box in boxes:
                    if ball and rim:
                        break
                    # Bounding box
                    x1, y1, x2, y2 = box[0]

                    # Scale back up to original dimensions
                    x1, y1, x2, y2 = int(x1 * self.width/640), int(y1 * self.height/640), int(x2 * self.width/640), int(y2* self.height/640)
                    w, h = x2 - x1, y2 - y1

                    # Confidence
                    conf = math.ceil((box[1] * 100)) / 100

                    # Class Name
                    cls = int(box[2])
                    current_class = self.class_names[cls]

                    center = (int(x1 + w / 2), int(y1 + h / 2))

                    # Only create ball points if high confidence or near hoop
                    # if (conf > .4 or (inq_hoop_region(center, self.hoop_pos) and conf > 0.2)) and current_class == "Ball":
                    #     self.ball_pos.append((center, self.frame_count, w, h, conf))
                    #     cvzone.cornerRect(self.frame, (x1, y1, w, h))

                    # # Create hoop points if high confidence
                    # if conf > .2 and current_class == "Hoop":
                    #     self.hoop_pos.append((center, self.frame_count, w, h, conf))
                    #     cvzone.cornerRect(self.frame, (x1, y1, w, h))

                    if (conf > 0.5 and current_class == 'rim' and not rim) or (conf > 0.55 and current_class == 'ball' and not ball):

                        label = f"{current_class}: {conf}"
                        color = self.colors[cls]

                        self.frame = cv2.rectangle(self.frame, (x1, y1), (x2, y2), color, 2)

                        (text_w, text_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
                        self.frame = cv2.rectangle(self.frame, (x1, y1 - 20), (x1 + text_w, y1), color, -1)
                        self.frame = cv2.putText(self.frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
                        
                        if current_class == 'rim':
                            rim = True
                            self.hoop_pos.append((center, self.frame_count, w, h, conf))
                        elif current_class == 'ball':
                            ball = True
                            self.ball_pos.append((center, self.frame_count, w, h, conf))

            self.clean_motion()
            self.shot_detection()
            self.display_score()
            self.frame_count += 1

            if self.hoop_pos:
                # draw up-region
                x1 = self.hoop_pos[-1][0][0] - 4 * self.hoop_pos[-1][2]
                x2 = self.hoop_pos[-1][0][0] + 4 * self.hoop_pos[-1][2]
                y1 = self.hoop_pos[-1][0][1] - 2 * self.hoop_pos[-1][3]
                y2 = self.hoop_pos[-1][0][1]

                pts = np.array([[x1, y1], [x2,y1], [x2, y2], [x1, y2]], np.int32)
 
                pts = pts.reshape((-1, 1, 2))

                self.frame = cv2.polylines(self.frame, [pts], True, (0, 255, 0), 3)

                # draw hoop-region
                x1 = self.hoop_pos[-1][0][0] - 0.7 * self.hoop_pos[-1][2]
                x2 = self.hoop_pos[-1][0][0] + 0.7 * self.hoop_pos[-1][2]
                y1 = self.hoop_pos[-1][0][1] - 1.5 * self.hoop_pos[-1][3]
                y2 = self.hoop_pos[-1][0][1] + 0.2 * self.hoop_pos[-1][3]

                pts = np.array([[x1, y1], [x2,y1], [x2, y2], [x1, y2]], np.int32)
 
                pts = pts.reshape((-1, 1, 2))

                self.frame = cv2.polylines(self.frame, [pts], True, (255, 0, 255), 3)

                # # draw down-region
                hoop_x1 = self.hoop_pos[-1][0][0] - 0.5 * self.hoop_pos[-1][2]
                hoop_x2 = self.hoop_pos[-1][0][0] + 0.5 * self.hoop_pos[-1][2]
                hoop_y = self.hoop_pos[-1][0][1] + 0.5 * self.hoop_pos[-1][3]
                y_range = 2 * self.hoop_pos[-1][3]
                alpha = 0.3

                x1 = hoop_x1 - y_range* alpha
                x4 = hoop_x2 + y_range * alpha

                pts = np.array([[x1, hoop_y + y_range], [hoop_x1, hoop_y], [hoop_x2, hoop_y], [x4, hoop_y + y_range]], np.int32)
                pts = pts.reshape((-1, 1, 2))

                self.frame = cv2.polylines(self.frame, [pts], True, (0, 0, 255), 3)

            # if self.screen_shot:
            #     cv2.imwrite(f"{screenshot_path}/{self.screen_shot_count}.png", self.frame)
            #     self.screen_shot = False
            #     self.screen_shot_count += 1


            cv2.imshow('Frame', self.frame)

            # Close if 'q' is clicked
            if cv2.waitKey(1) & 0xFF == ord('q'):  # higher waitKey slows video down, use 1 for webcam
                break


        self.cap.release()
        cv2.destroyAllWindows()

    def clean_motion(self):
        # Clean and display ball motion
        self.ball_pos = clean_ball_pos(self.ball_pos, self.frame_count)
        for i in range(0, len(self.ball_pos)):
            color = (0, 0, 255) if i == len(self.ball_pos)-1 else (100, 100, 100, 0.5)
            thickness = 5 if i == len(self.ball_pos)-1 else 2
            cv2.circle(self.frame, self.ball_pos[i][0], 2, color, thickness)

        # Clean hoop motion and display current hoop center
        if len(self.hoop_pos) > 1:
            self.hoop_pos = clean_hoop_pos(self.hoop_pos)
            cv2.circle(self.frame, self.hoop_pos[-1][0], 2, (128, 128, 0), 2)

    def shot_detection(self):
        if len(self.hoop_pos) > 0 and len(self.ball_pos) > 0:
            # Detecting when ball is in 'up' and 'down' area - ball can only be in 'down' area after it is in 'up'
            # if self.frame is not None:
            #     if self.up:
            #         self.frame = cv2.putText(self.frame, 'UP', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            #     elif self.down:
            #         self.frame = cv2.putText(self.frame, 'DOWN', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            #TODO: modify up state to only be true when ball is near the hoop
            self.up = detect_up(self.ball_pos, self.hoop_pos)
            if self.up:
                # self.attempts += 1
                self.up_frame = self.ball_pos[-1][1]
                self.frame = cv2.putText(self.frame, 'UP', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

            #TODO: modify down state to be true when ball is in area under hoop
            if self.up_frame and self.frame_count - self.up_frame < 48:
                self.down = detect_down(self.ball_pos, self.hoop_pos)
                if self.down:
                    self.frame = cv2.putText(self.frame, 'DOWN', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                    self.makes += 1
                    self.up = False
                    self.down = False
                    self.up_frame = None
                    # self.overlay_color = (0, 255, 0)
                    # self.fade_counter = self.fade_frames
            else:
                self.up_frame = None
                # self.overlay_color = (0, 0, 255)
                # self.fade_counter = self.fade_frames


                    
            # TODO: Modify scoring condition -> when down state occurs after up state
            # If ball goes from 'up' area to 'down' area in that order, increase attempt and reset
            # if self.frame_count % 10 == 0:
            #     if self.up and self.down and self.up_frame < self.down_frame:
            #         self.attempts += 1
            #         self.up = False
            #         self.down = False
            #         self.overlay_color = (0, 255, 0)
            #         self.fade_counter = self.fade_frames

            #         # If it is a make, put a green overlay
            #         score_res = score(self.ball_pos, self.hoop_pos)
            #         print(score_res)
            #         self.screen_shot = True
            #         if score_res:
            #             score_t, self.line = score_res
            #             self.line_frames = 25
            #             if score_t:
            #                 self.makes += 1
            #                 self.overlay_color = (0, 255, 0)
            #                 self.fade_counter = self.fade_frames

            #             # If it is a miss, put a red overlay
            #             else:
            #                 self.overlay_color = (0, 0, 255)
            #                 self.fade_counter = self.fade_frames

    def display_score(self):
        # Add text
        text = str(self.makes) + " / " + str(self.attempts)
        cv2.putText(self.frame, text, (50, 125), cv2.FONT_HERSHEY_SIMPLEX, 3, (255, 255, 255), 6)
        cv2.putText(self.frame, text, (50, 125), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 0), 3)

        # Gradually fade out color after shot
        if self.fade_counter > 0:
            alpha = 0.2 * (self.fade_counter / self.fade_frames)
            self.frame = cv2.addWeighted(self.frame, 1 - alpha, np.full_like(self.frame, self.overlay_color), alpha, 0)
            self.fade_counter -= 1


if __name__ == "__main__":
    ShotDetector()

