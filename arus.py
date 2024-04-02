from typing import Dict, Optional


import cv2
import numpy as np
import os

from ultralytics import YOLO
from database import insert
from supervision.detection.core import Detections
from supervision.draw.color import Color
from supervision.geometry.core import Point, Rect, Vector


class GarisArus:

    def __init__(self, start: Point, end: Point):
        self.vector = Vector(start=start, end=end)
        self.box_state: Dict[str, bool] = {}
        self.model = YOLO("yolov8n.pt")

    def arah(self,filename: str, frame: np.ndarray, detections: Detections, viodirs:str):

        for xyxy, _, confidence, class_id, tracker_id in detections:
            # handle detections with no tracker_id
            if tracker_id is None:
                continue

            # we check if all four anchors of bbox are on the same side of vector
            x1, y1, x2, y2 = xyxy
            anchors = [
                Point(x=x1, y=y1),
                Point(x=x1, y=y2),
                Point(x=x2, y=y1),
                Point(x=x2, y=y2),
            ]
            boxpassed = [self.vector.is_in(point=anchor) for anchor in anchors]

            # detection is partially in and partially out
            if len(set(boxpassed)) == 2:
                continue

            box_state = boxpassed[0]
            # handle new detection
            if tracker_id not in self.box_state:
                self.box_state[tracker_id] = box_state
                continue

            # handle detection on the same side of the line
            if self.box_state.get(tracker_id) == box_state:
                continue

            self.box_state[tracker_id] = box_state
            if box_state:
                if not os.path.exists(f'{viodirs}{filename[:-4]}/'):
                    os.mkdir(f'{viodirs}{filename[:-4]}/')
                cv2.putText(frame, "Melawan Arus", (int(((x2-x1)/2)+x1), int(((y2-y1)/2)+y1)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)
                cv2.imwrite(f'{viodirs}{filename[:-4]}/{filename[:-4]}-melanggar arus id-{tracker_id}.jpg', frame) 
                insert(jenis="Melanggar arus", nama_file=f"{filename}", kendaraan={self.model.model.names[class_id]}) 
                