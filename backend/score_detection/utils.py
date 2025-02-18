import math
import numpy as np


# TODO: modify line method, use time between reaching up and down regions instead
def score(ball_pos, hoop_pos):
    x = []
    y = []

    if len(hoop_pos) < 1 or len(ball_pos) < 2:
        return (False, None)
    
    rim_height = hoop_pos[-1][0][1] - 0.5 * hoop_pos[-1][3]

    # Get first point above rim and first point below rim
    for i in reversed(range(len(ball_pos))):
        if ball_pos[i][0][1] < rim_height:
            try:
                x.append(ball_pos[i][0][0])
                y.append(ball_pos[i][0][1])
                x.append(ball_pos[i+1][0][0])
                y.append(ball_pos[i+1][0][1])
                break
            except:
                print("exception")
                return (False, None)
            
    if not x or not y:
        return (False, None)
    
    points = ((x[0], y[0]), (x[1], y[1]))

    # Create line from two points
    if len(x) > 1:
        m, b = np.polyfit(x, y, 1)
        # Checks if projected line fits between the ends of the rim {x = (y-b)/m}
        predicted_x = ((hoop_pos[-1][0][1] - 0.5*hoop_pos[-1][3]) - b)/m
        rim_x1 = hoop_pos[-1][0][0] - 0.4 * hoop_pos[-1][2]
        rim_x2 = hoop_pos[-1][0][0] + 0.4 * hoop_pos[-1][2]
        if rim_x1 < predicted_x < rim_x2:
            return (True, points)
        else:
            return (False, points)


# Detects if the ball is below the net - used to detect shot attempts
# TODO: modify down state condition
# self.hoop_pos.append((center, self.frame_count, w, h, conf))
# center: (x, y)
# self.frame_count: int
def detect_down(ball_pos, hoop_pos):
    # y = hoop_pos[-1][0][1] + 0.5 * hoop_pos[-1][3]
    # ball_x =  ball_pos[-1][0][0]
    # hoop_x, hoop_w = hoop_pos[-1][0][0], hoop_pos[-1][-2]

    # x_diff = abs(hoop_x - ball_x) < 3 * hoop_w
    
    # if ball_pos[-1][0][1] > y and x_diff:
    #     return True
    # return False

    x, y = ball_pos[-1][0][0], ball_pos[-1][0][1]
    hoop_x1 = hoop_pos[-1][0][0] - 0.5 * hoop_pos[-1][2]
    hoop_x2 = hoop_pos[-1][0][0] + 0.5 * hoop_pos[-1][2]
    hoop_y = hoop_pos[-1][0][1] + 0.5 * hoop_pos[-1][3]
    y_diff = y - hoop_y

    y_range = 2 * hoop_pos[-1][3]
    alpha = 0.3

    if hoop_y <= y <= hoop_y + y_range and hoop_x1 - alpha * y_diff <= x <= hoop_x2 + alpha * y_diff:
        return True
    
    return False




# Detects if the ball is around the backboard - used to detect shot attempts
# TODO: modify up state condition
# self.hoop_pos.append((center, self.frame_count, w, h, conf))
# center: (x, y)
# self.frame_count: int

def detect_up(ball_pos, hoop_pos):
    x1 = hoop_pos[-1][0][0] - 2 * hoop_pos[-1][2]
    x2 = hoop_pos[-1][0][0] + 2  * hoop_pos[-1][2]
    y1 = hoop_pos[-1][0][1] - 2 * hoop_pos[-1][3]
    y2 = hoop_pos[-1][0][1]

    if x1 < ball_pos[-1][0][0] < x2 and y1 < ball_pos[-1][0][1] < y2 - 0.5 * hoop_pos[-1][3]:
        return True
    return False


# Checks if center point is near the hoop
# def in_hoop_region(center, hoop_pos):
#     if len(hoop_pos) < 1:
#         return False
#     x = center[0]
#     y = center[1]

#     x1 = hoop_pos[-1][0][0] - 0.7 * hoop_pos[-1][2]
#     x2 = hoop_pos[-1][0][0] + 0.7 * hoop_pos[-1][2]
#     y1 = hoop_pos[-1][0][1] - 1.5 * hoop_pos[-1][3]
#     y2 = hoop_pos[-1][0][1] + 0.2 * hoop_pos[-1][3]

#     if x1 < x < x2 and y1 < y < y2:
#         return True
#     return False

def in_score_region(ball_pos, hoop_pos):
    if len(hoop_pos) < 1 or len(ball_pos) < 1:
        return False
    
    x = ball_pos[-1][0][0]
    y = ball_pos[-1][0][1]

    x1 = hoop_pos[-1][0][0] - 2 * hoop_pos[-1][2]
    x2 = hoop_pos[-1][0][0] + 2 * hoop_pos[-1][2]
    y1 = hoop_pos[-1][0][1] - 3.5 * hoop_pos[-1][3]
    y2 = hoop_pos[-1][0][1] + 0.9 * hoop_pos[-1][3]

    return (x1 < x < x2 and y1 < y < y2)

# Removes inaccurate data points
# TODO: improve noise filtering
def clean_ball_pos(ball_pos, frame_count):
    # Removes inaccurate ball size to prevent jumping to wrong ball
    if len(ball_pos) > 1:
        # Width and Height
        w1 = ball_pos[-2][2]
        h1 = ball_pos[-2][3]
        w2 = ball_pos[-1][2]
        h2 = ball_pos[-1][3]

        # X and Y coordinates
        x1 = ball_pos[-2][0][0]
        y1 = ball_pos[-2][0][1]
        x2 = ball_pos[-1][0][0]
        y2 = ball_pos[-1][0][1]

        # Frame count
        f1 = ball_pos[-2][1]
        f2 = ball_pos[-1][1]
        f_dif = f2 - f1

        dist = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

        max_dist = 4 * math.sqrt((w1) ** 2 + (h1) ** 2)

        # Ball should not move a 4x its diameter within 5 frames
        if (dist > max_dist) and (f_dif < 3):
            ball_pos.pop()

        # Ball should be relatively square
        # elif (w2*1.4 < h2) or (h2*1.4 < w2):
        #     ball_pos.pop()

    #only care about points within score region

    # Remove points older than 30 frames
    if len(ball_pos) > 0:
        if frame_count - ball_pos[0][1] > 90:
            ball_pos.pop(0)

    return ball_pos

def clean_hoop_pos(hoop_pos):
    # Prevents jumping from one hoop to another
    if len(hoop_pos) > 1:
        x1 = hoop_pos[-2][0][0]
        y1 = hoop_pos[-2][0][1]
        x2 = hoop_pos[-1][0][0]
        y2 = hoop_pos[-1][0][1]

        w1 = hoop_pos[-2][2]
        h1 = hoop_pos[-2][3]
        w2 = hoop_pos[-1][2]
        h2 = hoop_pos[-1][3]

        f1 = hoop_pos[-2][1]
        f2 = hoop_pos[-1][1]

        f_dif = f2-f1

        dist = math.sqrt((x2-x1)**2 + (y2-y1)**2)

        max_dist = 0.5 * math.sqrt(w1 ** 2 + h1 ** 2)

        # Hoop should not move 0.5x its diameter within 5 frames
        if dist > max_dist and f_dif < 5:
            hoop_pos.pop()

        # # Hoop should be relatively square
        # if (w2*1.3 < h2) or (h2*1.3 < w2):
        #     hoop_pos.pop()

    # Remove old points
    if len(hoop_pos) > 40:
        hoop_pos.pop(0)

    return hoop_pos

def detect_score(ball_pos, hoop_pos, last_pos):
    #last item in ball_pos is the first ball position in down region
    #up_pos is the last ball position in up region
    #check if it crosses the hoop
    # down_pos = ball_pos[-1][0]
    # down_x, down_y = down_pos[0], down_pos[1]
    # up_x, up_y = up_pos[0], up_pos[1]
    # hoop_l, hoop_r = hoop_pos[-1][0][0] - 0.5 * hoop_pos[-1][2], hoop_pos[-1][0][0] + 0.5 * hoop_pos[-1][2]
    # hoop_y = hoop_pos[-1][0][1]

    # slope = (down_y - up_y) / (down_x - up_x)
    # delta_y = hoop_y - up_y
    # int_x = up_x + delta_y/slope

    # print(hoop_l, int_x, hoop_r)

    # return hoop_l < int_x < hoop_r
    if len(ball_pos) < 2:
        return False
    
    pos2 = ball_pos[-1][0]
    pos1 = last_pos[0]

    x1, y1 = pos1[0], pos1[1]
    x2, y2 = pos2[0], pos2[1]

    if x1 == x2 or y1 == y2:
         return False

    # ball has to be moving down
    if y1 > y2:
        return False

    hoop_l, hoop_r = hoop_pos[-1][0][0] - 0.3 * hoop_pos[-1][2], hoop_pos[-1][0][0] + 0.3 * hoop_pos[-1][2]
    hoop_y_mid = hoop_pos[-1][0][1]
    hoop_h = hoop_pos[-1][3]

    hoop_y1, hoop_y2 = hoop_y_mid - 0.3*hoop_h, hoop_y_mid + 0.3*hoop_h

    #if both points are inside the hoop box, it is definitely a score
    if (hoop_l < x1 < hoop_r) and (hoop_l < x2 < hoop_r) and (hoop_y1 < y1 < hoop_y2) and (hoop_y1 < y2 < hoop_y2):
        return True

    #otherwise, one point is outside the box, use linear interpolation to see if it interescts the hoop
    if y1 < hoop_y_mid and y2 > hoop_y_mid:
    
        slope = (y2 - y1) / (x2 - x1)
        delta_y = hoop_y_mid - y1
        intersect_x = x1 + delta_y/slope


        return hoop_l < intersect_x < hoop_r
    
    return False

    
def calculate_iou(box1, box2):
    x1, y1, x2, y2 = box1
    x1_, y1_, x2_, y2_ = box2

    xi1 = max(x1, x1_)
    yi1 = max(y1, y1_)
    xi2 = min(x2, x2_)
    yi2 = min(y2, y2_)

    inter_area = max(0, xi2 - xi1) * max(0, yi2 - yi1)
    box1_area = (x2 - x1) * (y2 - y1)
    box2_area = (x2_ - x1_) * (y2_ - y1_)

    union_area = box1_area + box2_area - inter_area

    iou = inter_area / union_area
    return iou

def convert_yolo_bbox_to_xyxy(bbox, img_width, img_height):
    x_center, y_center, width, height = bbox
    x1 = int((x_center - width / 2) * img_width)
    y1 = int((y_center - height / 2) * img_height)
    x2 = int((x_center + width / 2) * img_width)
    y2 = int((y_center + height / 2) * img_height)
    return x1, y1, x2, y2

