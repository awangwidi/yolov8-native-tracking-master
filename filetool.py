import shutil

def movefile(vid, dirvid, viodir):
    for vids in vid:
        shutil.copy(f"{dirvid}{vids[0]}", f"{viodir}{vids[0][:-4]}/{vids[0]}")
