import subprocess

mkvi = "/usr/bin/mkvinfo"


def mkv_get_info(u):
    h2 = "-1"
    w2 = "-1"
    hdv = str()
    codec = "-1"
    infchk = mkvi + " " + str(u)
    get_info = subprocess.Popen(infchk, shell=True, stdout=subprocess.PIPE)
    get_info_return = get_info.stdout.read()
    sort_info = get_info_return.decode("utf-8").split("\n")
    for info in sort_info:
        if info.startswith("(MKVInfo) No EBML head found."):
            print("Error, not MKV or readable")
            hdv = "Error"
            codec = "Error"
            continue
        if "Pixel width" in info:
            winf1 = info.split(":")
            w2 = winf1[1].lstrip()
        if "Pixel height" in info:
            hinf1 = info.split(":")
            h2 = hinf1[1].lstrip()
        #
        # ERROR set for identification purposes - maybe correct later
        #
    # something
    #
    hdv = w2 + "x" + h2

    for ino in sort_info:
        if "Codec ID" in ino:
            # print(sort_info)
            if "HEVC" in ino:
                # print("hevc: ", ino)
                codec = "x265"
                break
            elif "AVC" in ino:
                codec = "x264"
                break
            else:
                print("Video codec not identified")
    return hdv, codec
