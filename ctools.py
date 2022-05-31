import re
import os
from pymediainfo import MediaInfo


class clean:
    def __init__(self):
        pass

    def get_media_info(u):
        height = -1
        width = -1
        codec = -1
        if re.match(r".+\.(?:mkv|m4v|mpg|mp4)$", str(u)):
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
            print("something is broken in ctools -> get_media_info")
            print("broke reading filename: {}".format(u))
            print("height is: {}".format(height))
            print("width is: {}".format(width))
            print("codec is: {}".format(codec))
            quit()
        return resolution, codec

    def fname_rename(iterable_file_list):
        for ele_ment in iterable_file_list:
            if ele_ment.endswith("/"):
                continue
            if str(ele_ment).endswith(".part"):
                continue
            f_Name = ele_ment
            f_change_needed = 0
            rename_list = open("rename_list.txt", "r", encoding="utf8")
            # match and rename Directories first
            f_Name = f_Name.replace(" ", ".")
            if re.match(r"^\/(.+)([\/])$", ele_ment):
                for rename_list_item in rename_list:
                    rename_item = rename_list_item.rstrip()
                    if rename_item in f_Name:
                        f_Name = f_Name.replace(rename_item, ".")
                        f_change_needed = 1
                if f_change_needed == 1:
                    os.rename(ele_ment, f_Name)
                    continue
            if not re.match(r".+\.(?:mp4|mkv|avi|m4v|mov|mpg)$", ele_ment):
                continue
            for rename_list_item in rename_list:
                rename_item = rename_list_item.rstrip()
                if rename_item in f_Name:
                    f_Name = f_Name.replace(rename_item, ".")
                    f_change_needed = 1
            if f_change_needed == 1:
                os.rename(ele_ment, f_Name)


class c_mkv(clean):
    def __init__(self):
        self.mkv = {"mkv": {}}


class c_mp4(clean):
    def __init__(self):
        self.mp4 = {"mp4": {}}


class c_avi(clean):
    def __init__(self):
        self.avi = {"avi": {}}


class c_dst(clean):
    def __init__(self):
        self.dst = {"dst": {}}
