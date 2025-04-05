# shot_localizer.py

import numpy as np
import cv2

class ShotLocalizer:
    def __init__(self, penalty_box_points, image_dimensions):
        """
        Initialize localizer with penalty box corner points
        
        Args:
            penalty_box_points: List of 4 corner points [top-left, top-right, bottom-right, bottom-left]
            image_dimensions: Image dimensions as (width, height)
        """
        self.penalty_box_points = self._parse_points(penalty_box_points)
        self.image_width, self.image_height = self._parse_dimensions(image_dimensions)
        
        # Standard court dimensions (in some unit, e.g. feet)
        # These represent the same four corners on a standardized court diagram
        # TODO: hard-coded penalty box coords, maybe single template or mapped template
        self.court_penalty_box = np.array([
            [252, 24],    # top-left
            [485, 24],    # top-right
            [252, 300],    # bottom-right
            [485, 300]     # bottom-left
        ], dtype=float)
        
        # Calculate the homography matrix when initialized
        self.shot_data = []
        self.homography_matrix = self._calculate_homography()
    
    def _parse_points(self, points_str):
        """Parse comma-separated string of points into numpy array"""
        if isinstance(points_str, str):
            # Format: "x1,y1,x2,y2,x3,y3,x4,y4"
            # TODO: check if need to rescale with imagedimensions
            coords = list(map(float, points_str.split(',')))
            return np.array([
                [coords[0], coords[1]],  # top-left
                [coords[2], coords[3]],  # top-right
                [coords[4], coords[5]],  # bottom-right
                [coords[6], coords[7]]   # bottom-left
            ], dtype=float)
        elif isinstance(points_str, list):
            # Already in list format
            return np.array(points_str, dtype=np.float32).reshape(4, 2)
        else:
            raise ValueError("Invalid format for penalty box points")
    
    def _parse_dimensions(self, dimensions_str):
        """Parse dimensions string into width and height"""
        if isinstance(dimensions_str, str):
            # Format: "width,height"
            return tuple(map(float, dimensions_str.split(',')))
        elif isinstance(dimensions_str, tuple) or isinstance(dimensions_str, list):
            # Already in tuple/list format
            return dimensions_str
        else:
            raise ValueError("Invalid format for image dimensions")
    
    def _calculate_homography(self):
        """Calculate homography matrix from penalty box to court coordinates"""
        return cv2.findHomography(self.penalty_box_points, self.court_penalty_box)[0]
    
    def map_to_court(self, point):
        """
        Map a point from video coordinates to court coordinates
        
        Args:
            point: (x, y) coordinates in the video
            
        Returns:
            (x, y) coordinates on the standardized court
        """
        # Convert point to proper format
        point = np.array([[point[0], point[1]]], dtype=float)
        
        # Apply perspective transformation
        transformed_point = cv2.perspectiveTransform(point.reshape(-1, 1, 2), self.homography_matrix)
        
        # Return as a simple tuple
        return (transformed_point[0][0][0], transformed_point[0][0][1])