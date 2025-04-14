# shot_localizer.py

import numpy as np
import cv2

from constants import (
    MAP_WIDTH,
    MAP_HEIGHT,
    BASKET_X,
    BASKET_Y,
    PENALTY_BOX_X1,
    PENALTY_BOX_X2,
    PENALTY_BOX_Y1,
    PENALTY_BOX_Y2,
    THREE_PT_LEFT,
    THREE_PT_RIGHT,
    THREE_PT_RADIUS,
    WING_ZONE_Y,
    NUM_ZONES,
)

from logger import (
    INFO,
    SOCKET,
    Logger
)

logger = Logger([
    INFO
])

class Shot:
    def __init__(self, timestamp, success, x, y, quarter=None, zone=None):
        self.timestamp = timestamp
        self.success = success
        self.x = x
        self.y = y
        self.quarter = quarter
        self.zone = zone

    def __repr__(self):
        return f"Shot(timestamp={self.timestamp}, success={self.success}, x={self.x}, y={self.y}, quarter={self.quarter}, zone={self.zone})"

class TeamStatistics:
    def __init__(self, quarters):
        self.shots = []
        self.quarters = quarters
        

    def add_shot(self, timestamp, success, x, y):
        zone = self.determine_zone(x, y)
        quarter = self.determine_quarter(timestamp)

        shot = Shot(timestamp, success, x, y, quarter, zone)

        logger.log(INFO, f"Added shot: {shot}")
        self.shots.append(shot)

        return shot

    def determine_zone(self, x, y):
        if not x or not y:
            return None
        
        if not (0 < x < MAP_WIDTH and 0 < y < MAP_HEIGHT):
            return None
        
        zone = None
        distance = np.sqrt((x - BASKET_X) ** 2 + (y - BASKET_Y) ** 2)
        
        is_three_pt = x < THREE_PT_LEFT or x > THREE_PT_RIGHT or distance > THREE_PT_RADIUS
        column = 1 if x < PENALTY_BOX_X1 else 2 if x < PENALTY_BOX_X2 else 3

        if not is_three_pt:
            if y > PENALTY_BOX_Y2:
                zone = 4
            else:
                zone = column
        else:
            if y < WING_ZONE_Y:
                if x < THREE_PT_LEFT:
                    zone = 8
                elif x > THREE_PT_RIGHT:
                    zone = 9
            else:
                zone = column + 4

        return zone

    def determine_is_three_pt(self, zone):
        return zone not in [1, 2, 3, 4]  # Zones 1-4 are not three-point shots
    
    def determine_quarter(self, timestamp):
        for i, quarter in enumerate(self.quarters):
            if timestamp < quarter:
                return i-1
        return len(self.quarters)-1
    
    def get_statistics_by_quarter(self):
        makes = [0] * len(self.quarters)
        attempts = [0] * len(self.quarters)

        for shot in self.shots:
            if shot.success:
                makes[shot.quarter] += 1
            attempts[shot.quarter] += 1

        return {
            'makes': makes,
            'attempts': attempts,
            'shooting_percentage': [ (makes[i] / attempts[i]) if attempts[i] > 0 else 0 for i in range(len(self.quarters))],
            'total_makes': sum(makes),
            'total_attempts': sum(attempts),
            'total_shooting_percentage': sum(makes) / sum(attempts) if sum(attempts) > 0 else 0
        }

    def get_statistics_by_location(self):
        zone_makes = [0] * NUM_ZONES
        zone_attempts = [0] * NUM_ZONES
        three_pt_makes = 0
        three_pt_attempts = 0
        two_pt_makes = 0
        two_pt_attempts = 0
        paint_area_makes = 0
        paint_area_attempts = 0
        
        for shot in self.shots:
            if not shot.zone:
                continue
            
            is_three_pt = self.determine_is_three_pt(shot.zone)
            is_paint_area = shot.zone == 2

            if shot.success:
                if is_three_pt:
                    three_pt_makes += 1
                else:
                    two_pt_makes += 1
                if is_paint_area:
                    paint_area_makes += 1
                zone_makes[shot.zone-1] += 1

            if is_three_pt:
                three_pt_attempts += 1
            else:
                two_pt_attempts += 1
            if is_paint_area:
                paint_area_attempts += 1
            zone_attempts[shot.zone-1] += 1
        
        return {
            'zone_makes': zone_makes,
            'zone_attempts': zone_attempts,
            'zone_shooting_percentage': [ (makes / attempts) if attempts > 0 else 0 for makes, attempts in zip(zone_makes, zone_attempts)], 
            'three_pt_makes': three_pt_makes,
            'three_pt_attempts': three_pt_attempts,
            'three_pt_shooting_percentage': three_pt_makes / three_pt_attempts if three_pt_attempts > 0 else 0,
            'two_pt_makes': two_pt_makes,
            'two_pt_attempts': two_pt_attempts,
            'two_pt_shooting_percentage': two_pt_makes / two_pt_attempts if two_pt_attempts > 0 else 0,
            'paint_area_makes': paint_area_makes,
            'paint_area_attempts': paint_area_attempts,
            'paint_area_shooting_percentage': paint_area_makes / paint_area_attempts if paint_area_attempts > 0 else 0,
        }

    def get_statistics(self):
        location = self.get_statistics_by_location()
        quarter = self.get_statistics_by_quarter()

        location.update(quarter)
        return location
        