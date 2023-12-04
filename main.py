import cv2
from typing import Dict
from ultralytics import YOLO
import supervision as sv
import numpy as np
import time
import os
import filetool
from speed import*
# from speed2 import*
from supervision.geometry.core import Vector


directory = "./Video Uji/"
videos = os.listdir(directory)
# video_info = sv.VideoInfo.from_video_path(directory)
colors= sv.ColorPalette.default

violator = []
x1, y1 = 1436,586
x2,y2 = 1804,1405
L1_END = sv.Point(1436,586)
L1_START =sv.Point(2201,528)
L2_END = sv.Point(184,1401)
L2_START = sv.Point(1804,1405)

def main():
    for video in videos:
        # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        # out = cv2.VideoWriter(f'output.avi', fourcc, 24, video_info.resolution_wh)
        speedline = SpeedTrap(start=L1_START,end=L1_END,start2=L2_START,end2=L2_END)
        # speedline_annotator = SpeedAnnotate(thickness=2, text_thickness=1, text_scale=0.5, custom_in_text=" ", custom_out_text="melanggar")
        # trap = VelocityTrap()
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )
        framecount = 0
        model = YOLO("yolov8l.pt")
        prev_frame_time = 0
        new_frame_time = 0
        for result in model.track(source=f"{directory}{video}", show=False, stream=True, agnostic_nms=True, tracker="bytetrack.yaml"):
            frame = result.orig_img
            detections = sv.Detections.from_yolov8(result)
            # print(speedline.timestamp)

            if result.boxes.id is not None:
                detections.tracker_id = result.boxes.id.cpu().numpy().astype(int)
            selected_classes = [2, 3]
            detections = detections[np.isin(detections.class_id, selected_classes)] # type: ignore
            # zones.trigger(detections=detections)


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
            # cv2.rectangle(img=frame, pt1=(x1, y1), pt2=(x2, y2), color=(255, 0, 0), thickness=-1)
            # trap.Trap(frame=frame, detections=detections)
            speedline.trigger(frame=frame, detections=detections, num_frame=framecount)
            speedline.trigger2(frame=frame, detections=detections, filename=video, num_frame=framecount)
            # speedline_annotator.lineannotate(frame=frame, line_counter=speedline)
            # line_counter.trigger(detections=detections)
            # line_annotator.annotate(frame=frame, line_counter=line_counter)
            cv2.namedWindow("yolov8", cv2.WINDOW_NORMAL)
            cv2.imshow("yolov8", frame)
            
            # print(violator)
            framecount+=1
            if (cv2.waitKey(30) == 27):
                break
        if speedline.vio_list != []:
            violator.append(speedline.vio_list)
    filetool.movefile(vid=violator)
    # video.clip(stamps=speedline.timestamp)

if __name__ == "__main__":
    main()