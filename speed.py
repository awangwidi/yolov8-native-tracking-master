from typing import Dict, List, Optional
from ultralytics import YOLO
import cv2
import numpy as np
import time
import datetime
import os


from database import insert
from supervision.detection.core import Detections
from supervision.draw.color import Color
from supervision.geometry.core import Point, Rect, Vector


class SpeedTrap:
    def __init__(self, start: Point, end: Point, start2: Point, end2: Point):
        self.vector = Vector(start=start, end=end)
        self.vector2 = Vector(start=start2, end=end2)
        self.tracker_state: Dict[int, bool] = {}
        self.tracker_state2: Dict[int,bool] = {}
        self.speed_state: Dict[int, bool] = {}
        self.first={}
        self.second={}
        self.elapsed={}
        self.a_speed_ms={}
        self.a_speed_kh={}
        self.vio_list=[]
        self.model = YOLO("yolov8n.pt")
    def trigger(self, frame: np.ndarray, detections: Detections, num_frame: int):
        
        for xyxy, _, confidence, class_id, tracker_id in detections:
            if tracker_id is None:
                continue

            x1, y1, x2, y2 = xyxy
            anchors = [
                Point(x=x1, y=y2),
                Point(x=x2, y=y2),
            ]
            triggers = [self.vector.is_in(point=anchor) for anchor in anchors]
            tracker_state = triggers[0]

            if tracker_id not in self.tracker_state:
                self.tracker_state[tracker_id] = tracker_state
                continue
            if self.tracker_state.get(tracker_id) == tracker_state:
                continue
            self.tracker_state[tracker_id] = tracker_state
            if tracker_state:
                self.first[tracker_id]=num_frame
                

    def trigger2(self, frame: np.ndarray, filename: str, detections: Detections, num_frame: int, distance: int, fps:int, viodirs:str):
        

        for xyxy, _, confidence, class_id, tracker_id in detections:
            # Menghindari error program saat tidak ada objek terdeteksi
            if tracker_id is None:
                continue
            
            # Deklarasi variabel untuk mengambil titik dari bounding box yang ada pada frame
            x1, y1, x2, y2 = xyxy
            anchors = [
                Point(x=x1, y=y2),
                Point(x=x2, y=y2),
            ]
            #Melakukan pengecekan apabila bounding box menyentuh titik cek kedua
            triggers2 = [self.vector2.is_in(point=anchor) for anchor in anchors]
            tracker_state2 = triggers2[0]

            #Deteksi pada saat ada lebih dari satu bounding box pada frame
            if tracker_id not in self.tracker_state2:
                self.tracker_state2[tracker_id] = tracker_state2
                continue

            if self.tracker_state2.get(tracker_id) == tracker_state2:
                continue
            self.tracker_state2[tracker_id] = tracker_state2

            try:
                if tracker_state2:
                    if self.first is not None:                    
                        self.elapsed[tracker_id]=num_frame - self.first[tracker_id] 
                        distance = distance # penetapan jarak dua titik cek
                        self.a_speed_ms[tracker_id] = distance / (self.elapsed[tracker_id]/fps)  
                        self.a_speed_kh[tracker_id] = self.a_speed_ms[tracker_id] * 3.6
                        
                        cv2.putText(frame, f"{str(int(self.a_speed_kh[tracker_id]))}km/h",
                                    (int(x2) - 5, int(y1))
                                    ,cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.75, (255, 255, 255), 2)

                        if self.a_speed_kh[tracker_id] > 30:
                            if not os.path.exists(f'{viodirs}{filename[:-4]}/'):
                                os.mkdir(f'{viodirs}{filename[:-4]}/')
                            cv2.imwrite(f'{viodirs}{filename[:-4]}/{filename[:-4]}-melanggar batas kecepatan id-{tracker_id}.jpg', frame) 
                            insert(jenis="Melanggar batas kecepatan", nama_file=f"{filename}", kendaraan={self.model.model.names[class_id]}) 
                            self.vio_list.append(filename)
            except:
                print("Vehicle Missed")


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