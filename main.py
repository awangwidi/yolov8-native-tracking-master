import cv2
from typing import Dict
from ultralytics import YOLO
import supervision as sv
import numpy as np
import time

from speed import*
from supervision.geometry.core import Vector


VIDEO = "venv/DTGD2.mp4"
video_info = sv.VideoInfo.from_video_path(VIDEO)
colors= sv.ColorPalette.default
detection_area = np.array([
[563, 146],[755, 142],[507, 718],[19, 486]
])
# [488, 1188],[1988, 1136]
L1_END = sv.Point(983,854)
L1_START =sv.Point(2105,805)
L2_END = sv.Point(488, 1188)
L2_START = sv.Point(1988, 1136)



def main():
    # line_counter = sv.LineZone(start=LINE_START, end=LINE_END)
    # line_annotator = sv.LineZoneAnnotator(thickness=2, text_thickness=1, text_scale=0.5, custom_in_text=" ", custom_out_text="melanggar")
    speedline = SpeedTrap(start=L1_START,end=L1_END, start2=L2_START, end2=L2_END)
    speedline_annotator = SpeedAnnotate(thickness=2, text_thickness=1, text_scale=0.5, custom_in_text=" ", custom_out_text="melanggar")
    zones = sv.PolygonZone(
        polygon=detection_area, 
        frame_resolution_wh=video_info.resolution_wh
    )

    box_annotator = sv.BoxAnnotator(
        thickness=2,
        text_thickness=1,
        text_scale=0.5
    )

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter('output.avi', fourcc, 24, video_info.resolution_wh)
    model = YOLO("yolov8n.pt")
    prev_frame_time = 0
    new_frame_time = 0

    for result in model.track(source=VIDEO, show=False, stream=True, agnostic_nms=True):
        frame = result.orig_img
        detections = sv.Detections.from_yolov8(result)

        # x1, y1, x2, y2 = detections.xyxy[result].astype(int)
        # print(f'{x1}')

        if result.boxes.id is not None:
            detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
        selected_classes = [2, 3]
        detections = detections[np.isin(detections.class_id, selected_classes)] # type: ignore
        zones.trigger(detections=detections)

        box_position = []
            
        #     box_position.append(anchors)

        # # print(f"{len(box_position)}")

        # sudut = []
        # for i in range(len(box_position)):
        #     id = box_position[i][0]
        #     x1 = box_position[i][1]
        #     y1 = box_position[i][2]
        #     x2 = box_position[i][3]
        #     y2 = box_position[i][4]

        #     p = [id, x1, y2]
        #     # print(f"{x1:0.2f}, {y2:0.2f}")
        #     sudut.append(p)

        # for i in range(len(sudut)):
        #     x1 = sudut[i][1]
        #     x2 = sudut[i][2]

            
        # # if corner 
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
        # text_anchor=sv.Point(x=7,y=7)
        # frame=sv.draw_text(scene=frame, text=f'FPS:{fps:.2f}',text_anchor=text_anchor, text_color=sv.Color.white(), text_scale=1, text_font=cv2.FONT_HERSHEY_SIMPLEX)
        # cv2.line(frame, L2_START, L2_END, (100, 255, 0), 3, cv2.LINE_AA)
        speedline.trigger(frame = frame, detections=detections)
        speedline_annotator.annotate(frame=frame, line_counter=speedline)
        # line_counter.trigger(detections=detections)
        # line_annotator.annotate(frame=frame, line_counter=line_counter)
        cv2.namedWindow("yolov8", cv2.WINDOW_NORMAL)
        cv2.imshow("yolov8", frame)
        
        out.write(frame)

        # [31, Point(x=968.5386, y=723.022), Point(x=968.5386, y=1020.4978), Point(x=1219.3613, y=723.022), Point(x=1219.3613, y=1020.4978)]]
        # 968,1019
        
        if (cv2.waitKey(30) == 27):
            break

if __name__ == "__main__":
    main()