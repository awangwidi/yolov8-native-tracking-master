from typing import Dict, List, Optional

import cv2
import numpy as np
import time
import datetime

from database import insert
from supervision.detection.core import Detections
from supervision.draw.color import Color
from supervision.geometry.core import Point, Rect, Vector


class SpeedTrap:
    """
    Count the number of objects that cross a line.
    """
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
        self.a_speed_ms={}
        self.a_speed_kh={}
        self.time1 = int
        self.time2 = int
        self.timestamp = []
    def trigger(self, frame: np.ndarray, detections: Detections):
        """
        Update the in_count and out_count for the detections that cross the line.

        Attributes:
            detections (Detections): The detections for which to update the counts.

        """
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
            triggers = [self.vector.is_in(point=anchor) for anchor in anchors]
            # detection is partially in and partially out
            if len(set(triggers)) == 2:
                continue

            tracker_state = triggers[0]
            # handle new detection
            if tracker_id not in self.tracker_state:
                self.tracker_state[tracker_id] = tracker_state
                continue

            # handle detection on the same side of the line
            if self.tracker_state.get(tracker_id) == tracker_state:
                continue

            self.tracker_state[tracker_id] = tracker_state

            if tracker_state:
                self.first=time.time()
                self.time1 = 1
                # while tracker_state2:
                #     print("1")
                #     tracker_state2 = triggers2[0]
                #     # handle new detection
                #     self.tracker_state2[tracker_id] = tracker_state2
                #     print(f"tracker_state2: {tracker_state2}")
                #     # handle detection on the same side of the line
                #     # if self.tracker_state2.get(tracker_id) == tracker_state2:
                #     #     continue
                #     print(f"tracker_state2.get()tracker_id: {self.tracker_state2.get(tracker_id)}")
                #     self.tracker_state2[tracker_id] = tracker_state2
                #     print(f"4")

                # print(f"{self.first}")

            # else:
            #     self.out_count += 1
            #     cv2.imwrite(f"salah_arah_id_{tracker_id}.png", frame)

    def trigger2(self, frame: np.ndarray, detections: Detections):
        """
        Update the in_count and out_count for the detections that cross the line.

        Attributes:
            detections (Detections): The detections for which to update the counts.

        """
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
            # print(f"xyxy: {x1}, {y1}, {x2}, {y2}")
            triggers2 = [self.vector2.is_in(point=anchor) for anchor in anchors]
            # detection is partially in and partially out
            if len(set(triggers2)) == 2:
                continue

            tracker_state2 = triggers2[0]
            # handle new detection
            if tracker_id not in self.tracker_state:
                self.tracker_state2[tracker_id] = tracker_state2
                continue

            # handle detection on the same side of the line
            if self.tracker_state2.get(tracker_id) == tracker_state2:
                continue

            self.tracker_state2[tracker_id] = tracker_state2

            if tracker_state2:
                self.time2 = 5
                if self.first is not None:
                    # self.second[tracker_id]=time.time()
                    self.elapsed[tracker_id]=time.time() - self.first # type: ignore
                    distance = 5 # meters
                    self.a_speed_ms[tracker_id] = distance / self.elapsed[tracker_id]
                    self.a_speed_kh[tracker_id] = self.a_speed_ms[tracker_id] * 24 * 3.6
                    if self.a_speed_kh[tracker_id] > 30:
                        insert(str(datetime.date.today()), jenis=f"Melanggar batas kecepatan {tracker_id}")
                iter = (self.time1, self.time2)
                self.timestamp.append(iter)
                        

                # if self.a_speed_kh[tracker_id] > 30:
                #     # insert(str(datetime.date.today()), "Melanggar batas kecepatan")
                #     RecordStart(frame=frame, begin=True, melanggar=True, id=tracker_id)
                # elif self.a_speed_kh[tracker_id] <= 30:
                #     RecordStart(frame=frame, begin=True, melanggar=False, id=tracker_id)
            # if self.a_speed_kh is not None and y1 < 2100:        
            #     cv2.putText(frame, f"{str(int(self.a_speed_kh[tracker_id]))}km/h", (int(x2) - 5, int(y1)),cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2)

    
                # while tracker_state2:
                #     print("1")
                #     tracker_state2 = triggers2[0]
                #     # handle new detection
                #     self.tracker_state2[tracker_id] = tracker_state2
                #     print(f"tracker_state2: {tracker_state2}")
                #     # handle detection on the same side of the line
                #     # if self.tracker_state2.get(tracker_id) == tracker_state2:
                #     #     continue
                #     print(f"tracker_state2.get()tracker_id: {self.tracker_state2.get(tracker_id)}")
                #     self.tracker_state2[tracker_id] = tracker_state2
                #     print(f"4")

                # print(f"{self.first}")
                    
            # else:
            #     self.out_count += 1
            #     cv2.imwrite(f"salah_arah_id_{tracker_id}.png", frame)            
    # def calculatespeed(self, frame: np.ndarray, detections: Detections):
    #     distance = 10 # meters
    #     a_speed_ms = distance / self.elapsed
    #     a_speed_kh = a_speed_ms * 3s.6
        


class SpeedAnnotate:
    def __init__(
        self,
        thickness: float = 2,
        color: Color = Color.white(),
        text_thickness: float = 2,
        text_color: Color = Color.black(),
        text_scale: float = 0.5,
        text_offset: float = 1.5,
        text_padding: int = 10,
        custom_in_text: Optional[str] = None,
        custom_out_text: Optional[str] = None,
    ):
        """
        Initialize the LineCounterAnnotator object with default values.

        Attributes:
            thickness (float): The thickness of the line that will be drawn.
            color (Color): The color of the line that will be drawn.
            text_thickness (float): The thickness of the text that will be drawn.
            text_color (Color): The color of the text that will be drawn.
            text_scale (float): The scale of the text that will be drawn.
            text_offset (float): The offset of the text that will be drawn.
            text_padding (int): The padding of the text that will be drawn.

        """
        self.thickness: float = thickness
        self.color: Color = color
        self.text_thickness: float = text_thickness
        self.text_color: Color = text_color
        self.text_scale: float = text_scale
        self.text_offset: float = text_offset
        self.text_padding: int = text_padding
        self.custom_in_text: str = custom_in_text # type: ignore
        self.custom_out_text: str = custom_out_text # type: ignore

    # def lineannotate(self, frame: np.ndarray, line_counter: SpeedTrap) -> np.ndarray:
    #     """
    #     Draws the line on the frame using the line_counter provided.

    #     Attributes:
    #         frame (np.ndarray): The image on which the line will be drawn.
    #         line_counter (LineCounter): The line counter that will be used to draw the line.

    #     Returns:
    #         np.ndarray: The image with the line drawn on it.

    #     """
    #     cv2.line(
    #         frame,
    #         line_counter.vector.start.as_xy_int_tuple(),
    #         line_counter.vector.end.as_xy_int_tuple(),
    #         self.color.as_bgr(),
    #         self.thickness,
    #         lineType=cv2.LINE_AA,
    #         shift=0,
    #     )
    #     cv2.circle(
    #         frame,
    #         line_counter.vector.start.as_xy_int_tuple(),
    #         radius=5,
    #         color=self.text_color.as_bgr(),
    #         thickness=-1,
    #         lineType=cv2.LINE_AA,
    #     )
    #     cv2.circle(
    #         frame,
    #         line_counter.vector.end.as_xy_int_tuple(),
    #         radius=5,
    #         color=self.text_color.as_bgr(),
    #         thickness=-1,
    #         lineType=cv2.LINE_AA,
    #     )

    #     #Draw second line edit
    #     cv2.line(
    #         frame,
    #         line_counter.vector2.start.as_xy_int_tuple(),
    #         line_counter.vector2.end.as_xy_int_tuple(),
    #         self.color.as_bgr(),
    #         self.thickness,
    #         lineType=cv2.LINE_AA,
    #         shift=0,
    #     )
    #     cv2.circle(
    #         frame,
    #         line_counter.vector2.start.as_xy_int_tuple(),
    #         radius=5,
    #         color=self.text_color.as_bgr(),
    #         thickness=-1,
    #         lineType=cv2.LINE_AA,
    #     )
    #     cv2.circle(
    #         frame,
    #         line_counter.vector2.end.as_xy_int_tuple(),
    #         radius=5,
    #         color=self.text_color.as_bgr(),
    #         thickness=-1,
    #         lineType=cv2.LINE_AA,
    #     )
        
    #     in_text = (
    #         f"{self.custom_in_text}: {line_counter.in_count}"
    #         if self.custom_in_text is not None
    #         else f"in: {line_counter.in_count}"
    #     )
    #     out_text = (
    #         f"{self.custom_out_text}: {line_counter.out_count}"
    #         if self.custom_out_text is not None
    #         else f"out: {line_counter.out_count}"
    #     )

    #     (in_text_width, in_text_height), _ = cv2.getTextSize(
    #         in_text, cv2.FONT_HERSHEY_SIMPLEX, self.text_scale, self.text_thickness
    #     )
    #     (out_text_width, out_text_height), _ = cv2.getTextSize(
    #         out_text, cv2.FONT_HERSHEY_SIMPLEX, self.text_scale, self.text_thickness
    #     )

    #     in_text_x = int(
    #         (line_counter.vector.end.x + line_counter.vector.start.x - in_text_width)
    #         / 2
    #     )
    #     in_text_y = int(
    #         (line_counter.vector.end.y + line_counter.vector.start.y + in_text_height)
    #         / 2
    #         - self.text_offset * in_text_height
    #     )

    #     out_text_x = int(
    #         (line_counter.vector.end.x + line_counter.vector.start.x - out_text_width)
    #         / 2
    #     )
    #     out_text_y = int(
    #         (line_counter.vector.end.y + line_counter.vector.start.y + out_text_height)
    #         / 2
    #         + self.text_offset * out_text_height
    #     )

    #     in_text_background_rect = Rect(
    #         x=in_text_x,
    #         y=in_text_y - in_text_height,
    #         width=in_text_width,
    #         height=in_text_height,
    #     ).pad(padding=self.text_padding)
    #     out_text_background_rect = Rect(
    #         x=out_text_x,
    #         y=out_text_y - out_text_height,
    #         width=out_text_width,
    #         height=out_text_height,
    #     ).pad(padding=self.text_padding)

    #     cv2.rectangle(
    #         frame,
    #         in_text_background_rect.top_left.as_xy_int_tuple(), # type: ignore
    #         in_text_background_rect.bottom_right.as_xy_int_tuple(),
    #         self.color.as_bgr(),
    #         -1,
    #     )
    #     cv2.rectangle(
    #         frame,
    #         out_text_background_rect.top_left.as_xy_int_tuple(), # type: ignore
    #         out_text_background_rect.bottom_right.as_xy_int_tuple(),
    #         self.color.as_bgr(),
    #         -1,
    #     )

    #     cv2.putText(
    #         frame,
    #         in_text,
    #         (in_text_x, in_text_y),
    #         cv2.FONT_HERSHEY_SIMPLEX,
    #         self.text_scale,
    #         self.text_color.as_bgr(),
    #         self.text_thickness,
    #         cv2.LINE_AA,
    #     )
    #     cv2.putText(
    #         frame,
    #         out_text,
    #         (out_text_x, out_text_y),
    #         cv2.FONT_HERSHEY_SIMPLEX,
    #         self.text_scale,
    #         self.text_color.as_bgr(),
    #         self.text_thickness,
    #         cv2.LINE_AA,
    #     )
    #     return frame
    

    # def velocitytext(
    #     self,
    #     frame: np.ndarray,
    #     detections: Detections,
    #     line_counter: SpeedTrap,
    #     labels: Optional[List[str]] = None,
    # ) -> np.ndarray:
    #     font = cv2.FONT_HERSHEY_SIMPLEX
    #     for i in range(len(detections)):
    #         x1, y1, x2, y2 = detections.xyxy[i].astype(int)
    #         class_id = (
    #             detections.class_id[i] if detections.class_id is not None else None
    #         )
            
    #         text = (
    #             f"{class_id}"
    #             if (labels is None or len(detections) != len(labels))
    #             else labels[i]
    #         )
    #         text_x = x1
    #         text_y = y2

    #         cv2.putText(
    #             img=frame,
    #             text=text,
    #             org=(text_x, text_y),
    #             fontFace=font,
    #             fontScale=self.text_scale,
    #             color=self.text_color.as_rgb(),
    #             thickness=self.text_thickness,
    #             lineType=cv2.LINE_AA,
    #         )
    #     return frame