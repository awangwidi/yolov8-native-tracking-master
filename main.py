import cv2
from typing import Dict
from ultralytics import YOLO
import supervision as sv
import numpy as np
import time
import video
from speed import*
from supervision.geometry.core import Vector


VIDEO = "venv/DTGD2.mp4"
video_info = sv.VideoInfo.from_video_path(VIDEO)
colors= sv.ColorPalette.default
detection_area = np.array([
[563, 146],[755, 142],[507, 718],[19, 486]
])

L1_END = sv.Point(983,854)
L1_START =sv.Point(2105,805)
L2_END = sv.Point(488, 1188)
L2_START = sv.Point(1988, 1136)


def main():
    # line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
    # line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5, custom_in_text=" ", custom_out_text="melanggar")
    # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    # out = cv2.VideoWriter(f'output.avi', fourcc, 24, video_info.resolution_wh)
    speedline = SpeedTrap(start=L1_START,end=L1_END,start2=L2_START,end2=L2_END)
    # speedline_annotator = SpeedAnnotate(thickness=2, text_thickness=1, text_scale=0.5, custom_in_text=" ", custom_out_text="melanggar")
    zones = sv.PolygonZone(
        polygon=detection_area, 
        frame_resolution_wh=video_info.resolution_wh
    )

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5
    )

    model = YOLO("yolov8n.pt")
    prev_frame_time = 0
    new_frame_time = 0
    current_frame = 0
    for result in model.track(source=VIDEO, show=False, stream=True, agnostic_nms=True, tracker="bytetrack.yaml"):
        frame = result.orig_img
        detections = sv.Detections.from_yolov8(result)

        # print(speedline.timestamp)
        
        if result.boxes.id is not None:
            detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
        selected_classes = [2, 3]
        detections = detections[np.isin(detections.class_id, selected_classes)] # type: ignore
        zones.trigger(detections=detections)
            
        
        labels = [
            f"{tracker_id} {model.model.names[class_id]} {confidence:0.2f}" # type: ignore
            for xyxy, mask, confidence, class_id, tracker_id
            in detections
        ]


        frame = box_annotator.annotate(
            scene=frame, 
            detections=detections,
            labels=labels
        )
        
        # Calculate FPS
        new_frame_time = time.time()
        fps = 1 / (new_frame_time - prev_frame_time)
        prev_frame_time = new_frame_time

        # Display FPS on frame
        cv2.putText(frame, f'FPS: {fps:.2f}', (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 3, cv2.LINE_AA)

        speedline.trigger(frame=frame, detections=detections)
        speedline.trigger2(frame=frame, detections=detections)
        # speedline_annotator.lineannotate(frame=frame, line_counter=speedline)
        # line_counter.trigger(detections=detections)
        # line_annotator.annotate(frame=frame, line_counter=line_counter)
        cv2.namedWindow("yolov8", cv2.WINDOW_NORMAL)
        cv2.imshow("yolov8", frame)
        
        
        if (cv2.waitKey(30) == 27):
            break
    video.clip(stamps=speedline.timestamp)

if __name__ == "__main__":
    main()