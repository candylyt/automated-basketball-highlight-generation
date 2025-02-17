import cv2
import torch
import math
from ultralytics import YOLO
from utils import calculate_iou

def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

# Load the trained model
model = YOLO("/home/fyp_gch6/candy/best_ba.pt").to("cuda")

# Open the video file
# video_path = "/home/fyp_gch6/candy/training/aia_boy.mp4"
video_path = "/home/fyp_gch6/candy/310_1738582460.mp4"

cap = cv2.VideoCapture(video_path)

# Get video properties
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Define codec and create VideoWriter object
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
output_path = 'contest.mp4'
out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

results = model.predict(video_path, imgsz=1280, stream=True, conf=0.5, verbose=False)

contested_shots = 0
uncontested_shots = 0
cooldown_frames = 0

# Threshold to determine contested vs uncontested shots
# TO DO: change to the 1.2x of the width of the defender
person_width = 85

# Process each frame
for r in results:
    frame = r.orig_img

    if cooldown_frames > 0:
        cooldown_frames -= 1
        out.write(frame)
        continue

    shooter_box = None
    rim_box = None
    ball_box = None
    person_boxes = []

    for box in r.boxes:
        if box.cls == 4:
            shooter_box = box.xywh[0].tolist()
        elif box.cls == 2:
            person_boxes.append(box.xywh[0].tolist())
        elif box.cls == 3:
            rim_box = box.xywh[0].tolist()
        elif box.cls == 0:
            ball_box = box.xywh[0].tolist()

    if shooter_box:
        print(r.boxes.cls)
        print(r.boxes.xywh)
        is_contested = False
        closest_person_1 = None
        closest_distance_1 = float('inf')
        closest_person_2 = None
        closest_distance_2 = float('inf')
        contested_defender_box = None

        # find the two closest people
        for person_box in person_boxes:
            distance = calculate_distance((person_box[0], person_box[1]), (shooter_box[0], shooter_box[1]))
            if closest_person_1:
                if distance < closest_distance_1:
                    closest_person_2 = closest_person_1
                    closest_distance_2 = closest_distance_1
                    closest_person_1 = person_box
                    closest_distance_1 = distance
                elif distance < closest_distance_2:
                    closest_person_2 = person_box
                    closest_distance_2 = distance
            else:
                closest_person_1 = person_box
                closest_distance_1 = distance

        if rim_box:
            # if rim is on the left hand side
            if (rim_box[0]-rim_box[2]/2) < (shooter_box[0]+shooter_box[2]/2):
                if closest_person_1[0] < closest_person_2[0]:
                    if closest_distance_1 <= person_width:
                        contested_defender_box = closest_person_1
                        is_contested = True
                else:
                    if closest_distance_2 <= person_width:
                        contested_defender_box = closest_person_2
                        is_contested = True
            # if rim is on the right hand side
            elif (rim_box[0]-rim_box[2]/2) > (shooter_box[0]+shooter_box[2]/2):
                if closest_person_1[0] > closest_person_2[0]:
                    if closest_distance_1 <= person_width:
                        contested_defender_box = closest_person_1
                        is_contested = True
                else:
                    if closest_distance_2 <= person_width:
                        contested_defender_box = closest_person_2
                        is_contested = True

        if is_contested:
            contested_shots += 1
            cv2.putText(frame, "Contested", (int(shooter_box[0]), int(shooter_box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            cv2.circle(frame, (int(rim_box[0]), int(rim_box[1])), 2, (128, 128, 0), 2)
            # Draw the bounding box for the contested defender
            cv2.rectangle(frame, (int(contested_defender_box[0]-contested_defender_box[2]/2), int(contested_defender_box[1]-contested_defender_box[3]/2)), (int(contested_defender_box[0]+contested_defender_box[2]/2), int(contested_defender_box[1]+contested_defender_box[3]/2)), (0, 0, 255), 2)
            cv2.rectangle(frame, (int(shooter_box[0]-shooter_box[2]/2), int(shooter_box[1]-shooter_box[3]/2)), (int(shooter_box[0]+shooter_box[2]/2), int(shooter_box[1]+shooter_box[3]/2)), (255, 0, 0), 2)
        else:
            uncontested_shots += 1
            cv2.putText(frame, "Uncontested", (int(shooter_box[0]), int(shooter_box[1]) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
            cv2.rectangle(frame, (int(closest_person_1[0]-closest_person_1[2]/2), int(closest_person_1[1]-closest_person_1[3]/2)), (int(closest_person_1[0]+closest_person_1[2]/2), int(closest_person_1[1]+closest_person_1[3]/2)), (255, 0, 0), 2)
            cv2.rectangle(frame, (int(closest_person_2[0]-closest_person_2[2]/2), int(closest_person_2[1]-closest_person_2[3]/2)), (int(closest_person_2[0]+closest_person_2[2]/2), int(closest_person_2[1]+closest_person_2[3]/2)), (0, 0, 255), 2)
            cv2.circle(frame, (int(rim_box[0]), int(rim_box[1])), 2, (128, 128, 0), 2)

        # Set cooldown frames to skip subsequent frames for 3 seconds
        cooldown_frames = int(fps * 3)

    out.write(frame)

# Release everything when done
cap.release()
out.release()
# cv2.destroyAllWindows()

print(f'Contested Shots: {contested_shots}, Uncontested Shots: {uncontested_shots}')