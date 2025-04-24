import math
import numpy as np
from datetime import timedelta, datetime

def in_score_region(ball_pos, hoop_pos):
    if len(hoop_pos) < 1 or len(ball_pos) < 1:
        return False
    
    x = ball_pos[-1][0][0]
    y = ball_pos[-1][0][1]

    x1 = hoop_pos[-1][0][0] - 2 * hoop_pos[-1][2]
    x2 = hoop_pos[-1][0][0] + 2 * hoop_pos[-1][2]
    y1 = hoop_pos[-1][0][1] - 5.5 * hoop_pos[-1][3]
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
    if len(ball_pos) < 2:
        return False
    
    hoop_l = hoop_pos[-1][0][0] - 0.5 * hoop_pos[-1][2]
    hoop_r = hoop_pos[-1][0][0] + 0.5 * hoop_pos[-1][2]
    hoop_t = hoop_pos[-1][0][1] - 0.5 * hoop_pos[-1][3]
    hoop_b = hoop_pos[-1][0][1] + 0.5 * hoop_pos[-1][3]

    
    pos2 = ball_pos[-1][0]
    pos1 = last_pos[0]

    x1, y1 = pos1[0], pos1[1]
    x2, y2 = pos2[0], pos2[1]

    if hoop_l < x2 < hoop_r and hoop_t < y2 < hoop_b:
        return True

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

def get_time_string(timestamp):
    timestamp = max(0, timestamp)

    t = str(timedelta(milliseconds=timestamp)).split('.')[0]
    return datetime.strptime(t, "%H:%M:%S").strftime('%H:%M:%S')