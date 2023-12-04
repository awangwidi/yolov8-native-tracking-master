from moviepy import editor as ed
from speed import*
from main import*

def clip(stamps):
    # count = 1
    # for stamp in stamps:
    # print(f"{stamp[0]}, {stamp[1]}")
    video = ed.VideoFileClip(VIDEO).subclip(1, )
    result = ed.CompositeVideoClip([video]) # Overlay text on video
    result.write_videofile(f"VideoPelanggar/Clip pelanggar ke-{count}.mp4",fps=24, codec="libx264")
    # count += 1

def timepicker():
    print("soon")