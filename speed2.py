import pandas as pd
import numpy as np
import cv2
import matplotlib.pyplot as plt

from supervision.detection.core import Detections
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from typing import Dict, List, Optional

import time
import datetime

class VelocityTrap:
    def __init__(self, start: Point, end: Point, start2: Point, end2: Point):
        """
        Initialize a LineCounter object.

        Attributes:
            start (Point): The starting point of the line.
            end (Point): The ending point of the line.

        """
        self.vector = Vector(start=start, end=end)
        self.vector2 = Vector(start=start2, end=end2)
        self.tracker_state: Dict[int, bool] = {}
        self.tracker_state2: Dict[int,bool] = {}
        self.in_count: int = 0
        self.out_count: int = 0
        self.first={}
        self.second={}
        self.elapsed={}
        self.a_speed_kh: float

    def Trap(self, frame: np.ndarray, detections: Detections):
        for xyxy, _, confidence, class_id, tracker_id in detections:
                # handle detections with no tracker_id
            if tracker_id is None:
                    continue
            roll = (200,100)
            polygon1 = Polygon([[983,854],[2105,805],[1988, 1136],[488, 1188]])
            if(polygon1.contains(Point(int(x+w/2),int(y+(h)/2)))):
                print("it's passed")