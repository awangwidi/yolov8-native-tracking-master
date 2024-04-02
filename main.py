import cv2
from typing import Dict
from ultralytics import YOLO
import supervision as sv
import numpy as np
import time
import os
import filetool
from speed import*
from arus import*
from supervision.geometry.core import Vector


directory = "./Video Uji/"
videos = os.listdir(directory)
vio_directory = "./VideoPelanggarFix/"

violator = []
#Garis pengukur kecepatan
L1_END = Point(1436,586)
L1_START = Point(2201,528)
L2_END = Point(184,1401)
L2_START = Point(1804,1405)

# DTGD FHD
# L1_END = sv.Point(717,293)
# L1_START = sv.Point(1100,264)
# L2_END = sv.Point(77,700)
# L2_START = sv.Point(903,701)

# L1_END = Point(649,822)
# L1_START = Point(1149,769)
# L2_END = Point(43,1173)
# L2_START = Point(1040,1040)

#Garis pendeteksi arah objek
# garis_arah1 = sv.Point(481,1186)
# garis_arah2 = sv.Point(1192,1137)

garis_arah1 = sv.Point(23,1213)
garis_arah2 = sv.Point(3075,1090)
def main():
    for video in videos:
        infovideo = cv2.VideoCapture(f"{directory}{video}")
        video_fps = infovideo.get(cv2.CAP_PROP_FPS)
        print(video_fps)
        # fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        # out = cv2.VideoWriter(f'output.avi', fourcc, video_fps, video_info.resolution_wh)
        speedline = SpeedTrap(start=L1_START,end=L1_END,start2=L2_START,end2=L2_END)
        arusline = GarisArus(start=garis_arah1, end=garis_arah2)
        jarak = 15
        box_annotator = sv.BoxAnnotator(
            thickness=2,
            text_thickness=1,
            text_scale=0.5
        )
        framecount = 0
        model = YOLO("yolov8l.pt")
        prev_frame_time = 0
        new_frame_time = 0
        for result in model.track(source=f"{directory}{video}", show=False, stream=True, agnostic_nms=True, save=True, tracker="bytetrack.yaml"):
            frame = result.orig_img
            detections = sv.Detections.from_yolov8(result)
            
            # print(speedline.timestamp)
            # cv2.line(frame, (1436,586), (2201,528), (255, 0, 0), 4)
            # cv2.line(frame, (184,1401), (1804,1405), (255, 0, 0), 4)

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
            # new_frame_time = time.time()
            # fps = 1 / (new_frame_time - prev_frame_time)
            # prev_frame_time = new_frame_time

            # Display FPS on frame
            # cv2.putText(frame, f'FPS: {fps:.2f}', (7, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (100, 255, 0), 3, cv2.LINE_AA)
            # cv2.rectangle(img=frame, pt1=(x1, y1), pt2=(x2, y2), color=(255, 0, 0), thickness=-1)
            # trap.Trap(frame=frame, detections=detections)
            speedline.trigger(frame=frame, detections=detections, num_frame=framecount)
            speedline.trigger2(frame=frame, detections=detections, filename=video, num_frame=framecount, distance=jarak, fps=video_fps, viodirs=vio_directory)
            arusline.arah(frame=frame, detections=detections, filename=video, viodirs=vio_directory) #Pemanggilan fungsi untuk mendeteksi apabila terdapat kendaraan yang melawan arus

            # arusline.arah(detections=detections)
            # speedline_annotator.lineannotate(frame=frame, line_counter=speedline)
            # line_counter.trigger(detections=detections)
            # line_annotator.annotate(frame=frame, line_counter=line_counter)
            cv2.namedWindow("yolov8", cv2.WINDOW_NORMAL)
            cv2.imshow("yolov8", frame)
            # cv2.imwrite('captuer ez.jpg', frame)
            # print(violator)
            framecount+=1
            if (cv2.waitKey(30) == 27):
                break
        # out.write(frame)
        if speedline.vio_list != []:
            violator.append(speedline.vio_list)
    filetool.movefile(vid=violator, dirvid=directory, viodir=vio_directory)
    # video.clip(stamps=speedline.timestamp)

if __name__ == "__main__":
    main()