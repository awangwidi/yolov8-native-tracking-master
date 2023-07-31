import cv2
import numpy as np
import supervision as sv
import os

import main

def RecordStart(frame: np.ndarray, begin: bool, melanggar: bool, id: int):
    video = main.VIDEO
    video_info = sv.VideoInfo.from_video_path(video)
    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(f'melanggar {id}.avi', fourcc, 24, video_info.resolution_wh)
    if begin:
        if melanggar is True:
            out.write(frame)
        elif melanggar is False:
            os.remove(f"/melanggar {id}.avi")
            if out.isOpened():
                out.release()