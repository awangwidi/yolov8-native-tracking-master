import os

def movefile(vid):
    for vids in vid:

        os.rename(f"./VideoPelanggar/{vids[0]}", f"./VideoPelanggarFix/{vids[0]}")
