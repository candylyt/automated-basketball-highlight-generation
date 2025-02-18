import cv2
import torch
import math
from ultralytics import YOLO
from utils import calculate_iou

def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

class ContestAnalyzer:
    def __init__(self, model_path="backend/score_detection/weights/best_ba.pt", device="cuda"):
        self.model = YOLO(model_path).to(device)
        self.person_width = 85  # Threshold to determine contested vs uncontested shots

    def analyze_video(self, video_path, output_path=None, save_annotated=False):
        cap = cv2.VideoCapture(video_path)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))

        writer = None
        if save_annotated and output_path:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

        contested_shots = 0
        uncontested_shots = 0
        cooldown_frames = 0

        results = self.model.predict(video_path, imgsz=1280, stream=True, conf=0.5, verbose=False)

        for r in results:
            frame = r.orig_img

            if cooldown_frames > 0:
                cooldown_frames -= 1
                if writer:
                    writer.write(frame)
                continue

            shooter_box = None
            rim_box = None
            ball_box = None
            person_boxes = []

            for box in r.boxes:
                if box.cls == 4:  # shooter
                    shooter_box = box.xywh[0].tolist()
                elif box.cls == 2:  # person
                    person_boxes.append(box.xywh[0].tolist())
                elif box.cls == 3:  # rim
                    rim_box = box.xywh[0].tolist()
                elif box.cls == 0:  # ball
                    ball_box = box.xywh[0].tolist()

            if shooter_box:
                is_contested, contested_defender_box = self._analyze_shot(shooter_box, person_boxes, rim_box)

                if is_contested:
                    contested_shots += 1
                    if save_annotated:
                        self._draw_contested_annotations(frame, shooter_box, rim_box, contested_defender_box)
                else:
                    uncontested_shots += 1
                    if save_annotated:
                        self._draw_uncontested_annotations(frame, shooter_box, rim_box, person_boxes[:2])

                # Set cooldown frames to skip subsequent frames for 3 seconds
                cooldown_frames = int(fps * 3)

            if writer:
                writer.write(frame)

        if writer:
            writer.release()
        cap.release()

        return {
            'contested_shots': contested_shots,
            'uncontested_shots': uncontested_shots,
            'total_shots': contested_shots + uncontested_shots
        }

    def _analyze_shot(self, shooter_box, person_boxes, rim_box):
        is_contested = False
        closest_person_1 = None
        closest_distance_1 = float('inf')
        closest_person_2 = None
        closest_distance_2 = float('inf')
        contested_defender_box = None

        # Find the two closest people
        for person_box in person_boxes:
            distance = calculate_distance(
                (person_box[0], person_box[1]), 
                (shooter_box[0], shooter_box[1])
            )
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

        if rim_box and closest_person_1 and closest_person_2:
            # If rim is on the left hand side
            if (rim_box[0]-rim_box[2]/2) < (shooter_box[0]+shooter_box[2]/2):
                if closest_person_1[0] < closest_person_2[0]:
                    if closest_distance_1 <= self.person_width:
                        contested_defender_box = closest_person_1
                        is_contested = True
                else:
                    if closest_distance_2 <= self.person_width:
                        contested_defender_box = closest_person_2
                        is_contested = True
            # If rim is on the right hand side
            elif (rim_box[0]-rim_box[2]/2) > (shooter_box[0]+shooter_box[2]/2):
                if closest_person_1[0] > closest_person_2[0]:
                    if closest_distance_1 <= self.person_width:
                        contested_defender_box = closest_person_1
                        is_contested = True
                else:
                    if closest_distance_2 <= self.person_width:
                        contested_defender_box = closest_person_2
                        is_contested = True

        return is_contested, contested_defender_box

    def _draw_contested_annotations(self, frame, shooter_box, rim_box, defender_box):
        # Draw "Contested" text
        cv2.putText(frame, "Contested", 
                   (int(shooter_box[0]), int(shooter_box[1]) - 10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        # Draw rim position
        cv2.circle(frame, (int(rim_box[0]), int(rim_box[1])), 2, (128, 128, 0), 2)
        
        # Draw defender box
        cv2.rectangle(frame, 
                     (int(defender_box[0]-defender_box[2]/2), int(defender_box[1]-defender_box[3]/2)),
                     (int(defender_box[0]+defender_box[2]/2), int(defender_box[1]+defender_box[3]/2)),
                     (0, 0, 255), 2)
        
        # Draw shooter box
        cv2.rectangle(frame,
                     (int(shooter_box[0]-shooter_box[2]/2), int(shooter_box[1]-shooter_box[3]/2)),
                     (int(shooter_box[0]+shooter_box[2]/2), int(shooter_box[1]+shooter_box[3]/2)),
                     (255, 0, 0), 2)

    def _draw_uncontested_annotations(self, frame, shooter_box, rim_box, closest_people):
        # Draw "Uncontested" text
        cv2.putText(frame, "Uncontested",
                   (int(shooter_box[0]), int(shooter_box[1]) - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        # Draw rim position
        cv2.circle(frame, (int(rim_box[0]), int(rim_box[1])), 2, (128, 128, 0), 2)
        
        # Draw closest people boxes
        for person_box in closest_people:
            cv2.rectangle(frame,
                         (int(person_box[0]-person_box[2]/2), int(person_box[1]-person_box[3]/2)),
                         (int(person_box[0]+person_box[2]/2), int(person_box[1]+person_box[3]/2)),
                         (255, 0, 0), 2)

if __name__ == "__main__":
    analyzer = ContestAnalyzer()
    results = analyzer.analyze_video(
        video_path="/home/fyp_gch6/candy/310_1738582460.mp4",
        output_path="contest_analysis.mp4",
        save_annotated=True
    )
    print(f'Contest Analysis Results:')
    print(f'Contested Shots: {results["contested_shots"]}')
    print(f'Uncontested Shots: {results["uncontested_shots"]}')
    print(f'Total Shots: {results["total_shots"]}')