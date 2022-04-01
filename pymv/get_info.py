import subprocess
from pymediainfo import MediaInfo

mkv_info = "/usr/bin/mkvinfo "


def mkv_get_info(u):
    h2 = "-1"
    w2 = "-1"
    hdv = str()
    codec = "-1"
    infchk = mkv_info + " " + str(u)
    get_info = subprocess.Popen(infchk, shell=True, stdout=subprocess.PIPE)
    get_info_return = get_info.stdout.read()
    sort_info = get_info_return.decode("utf-8").split("\n")
    for info in sort_info:
        if (h2 != "-1") and (w2 != "-1") and (codec != "-1"):
            break
        elif info.startswith("(mkv_infonfo) No EBML head found."):
            print("Error, not MKV or readable")
            hdv = "Error"
            codec = "Error"
            continue
        elif "Pixel width" in info:
            winf1 = info.split(":")
            w2 = winf1[1].lstrip()
        elif "Pixel height" in info:
            hinf1 = info.split(":")
            h2 = hinf1[1].strip()
        elif "Codec ID" in info:
            # print(sort_info)
            if "HEVC" in info:
                # print("hevc: ", ino)
                codec = "x265"
            elif "AVC" in info:
                codec = "x264"
            else:
                print("Video codec not identified")
    hdv = w2 + "x" + h2
    return hdv, codec


def mp4_get_info(u):
    h2 = "-1"
    w2 = "-1"
    hdv = str()
    codec = "-1"
    for track in MediaInfo.parse(u).tracks:
        if (h2 != "-1") and (w2 != "-1") and (codec != "-1"):
            break
        elif track.track_type == "Video":
            codec = track.format
            h2 = track.height
            w2 = track.width
    hdv = str(w2) + "x" + str(h2)
    return hdv, codec
