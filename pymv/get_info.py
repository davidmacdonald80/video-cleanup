from pymediainfo import MediaInfo
import re


def get_media_info(u):
    height = -1
    width = -1
    codec = -1
    if re.match(r".+\.(?:mkv|m4v|mpg|mp4)$", str(u)):
        # print("yes")
        # quit()
        for track in MediaInfo.parse(u).tracks:
            if codec != -1:
                break
            elif track.track_type == "Video":
                codec = track.format
    elif re.match(r".+\.(?:avi)$", str(u)):
        for track in MediaInfo.parse(u).tracks:
            if codec != -1:
                break
            elif track.track_type == "Video":
                codec = track.codec_id
    else:
        print("add extension and verify it pulls proper info")
        print("pymv.getinfo - get_media_info")
        quit()
    for track in MediaInfo.parse(u).tracks:
        if (height != -1) and (width != -1):
            break
        elif track.track_type == "Video":
            height = track.height
            width = track.width
    resolution = str(width) + "x" + str(height)
    if (height == -1) or (width == -1) or (codec == -1):
        print("something is broken in pymv.get_info.py-get_media_info")
        print("broke reading filename: {}".format(u))
        print("height is: {}".format(height))
        print("width is: {}".format(width))
        print("codec is: {}".format(codec))
        quit()
    return resolution, codec


# def mkv_get_info(u):
#     height = "-1"
#     width = "-1"
#     resolution = str()
#     codec = "-1"
#     for track in MediaInfo.parse(u).tracks:
#         if (height != "-1") and (width != "-1") and (codec != "-1"):
#             break
#         elif track.track_type == "Video":
#             codec = track.format
#             height = track.height
#             width = track.width
#     resolution = str(width) + "x" + str(height)
#     return resolution, codec
# infchk = mkv_info + " " + str(u)
# get_info = subprocess.Popen(infchk, shell=True, stdout=subprocess.PIPE)
# get_info_return = get_info.stdout.read()
# sort_info = get_info_return.decode("utf-8").split("\n")
# for info in sort_info:
#     if (height != "-1") and (width != "-1") and (codec != "-1"):
#         break
#     elif info.startswith("(mkv_infonfo) No EBML head found."):
#         print("Error, not MKV or readable")
#         resolution = "Error"
#         codec = "Error"
#         continue
#     elif "Pixel width" in info:
#         winf1 = info.split(":")
#         width = winf1[1].lstrip()
#     elif "Pixel height" in info:
#         hinf1 = info.split(":")
#         height = hinf1[1].strip()
#     elif "Codec ID" in info:
#         # print(sort_info)
#         if "HEVC" in info:
#             # print("hevc: ", ino)
#             codec = "x265"
#         elif "AVC" in info:
#             codec = "x264"
#         else:
#             print("Video codec not identified")
# resolution = width + "x" + height
# return resolution, codec


# def mp4_get_info(u):
#     height = "-1"
#     width = "-1"
#     resolution = str()
#     codec = "-1"
#     for track in MediaInfo.parse(u).tracks:
#         if (height != "-1") and (width != "-1") and (codec != "-1"):
#             break
#         elif track.track_type == "Video":
#             codec = track.format
#             height = track.height
#             width = track.width
#     resolution = str(width) + "x" + str(height)
#     return resolution, codec


# def avi_get_info(u):
#     height = "-1"
#     width = "-1"
#     resolution = str()
#     codec = "-1"
#     for track in MediaInfo.parse(u).tracks:
#         if (height != "-1") and (width != "-1") and (codec != "-1"):
#             break
#         elif track.track_type == "Video":
#             codec = track.codec_id
#             height = track.height
#             width = track.width
#     resolution = str(width) + "x" + str(height)
#     return resolution, codec
