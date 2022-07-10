import re
import os
import subprocess
from pymediainfo import MediaInfo
import string
import copy

# from clean_video import re_se, slsh, bcolors


class cvars:
    # start Win Vars
    win_slsh = "\\"
    win_mkv_info = '"c:\\Program Files\\MKVToolNix\\mkvinfo.exe"'
    win_mkv_e = '"c:\\Program Files\\MKVToolNix\\mkvextract.exe"'
    win_mkvmrg = '"c:\\Program Files\\MKVToolNix\\mkvmerge.exe"'
    win_mkvpedit = '"c:\\Program Files\\MKVToolNix\\mkvpropedit.exe"'
    win_ff_mpg = '"c:\\portables\\ffmpeg\\bin\\ffmpeg.exe" -hide_banner'
    win_ff_prob = "c:\\portables\\ffmpeg\\bin\\ffprobe.exe"
    win_destpath = "c:\\destp\\dst\\"
    win_ip = "c:\\srcpath\\Downloads\\"
    win_tmp11 = "c:\\tmp\\cleanvid\\"
    win_subpath = "c:\\destp\\sbs\\"
    win_logfile = "c:\\srcpath\\clean-move.log"
    # start nix vars
    nix_slsh = "/"
    nix_mkv_info = "/usr/bin/mkvinfo"
    nix_mkv_e = "/usr/bin/mkvextract"
    nix_mkvmrg = "/usr/bin/mkvmerge"
    nix_mkvpedit = "/usr/bin/mkvpropedit"
    nix_ff_mpg = "/usr/bin/ffmpeg -hide_banner"
    nix_ff_prob = "/usr/bin/ffprobe"
    nix_destpath_current = "/media/Videos/Current-Renewed.Seasons/"
    nix_destpath_ended = "/media/Videos/Ended-Cancelled.Seasons/"
    nix_subpath = "/media/Videos/subs/"
    nix_logfile = "/home/david/Downloads/clean-move.log"
    nix_ramdisk_ip = "/tmp/ramdisk/clean/"
    nix_ramdisk_tmp11 = "/tmp/ramdisk/tmp/"
    nix_ramdisk_trash11 = "/tmp/ramdisk/trash/"
    nix_ip = "/home/david/Downloads/jdownloader/"
    nix_tmp11 = "/tmp/cleanvid/"
    #
    # start other needed vars
    mkmer = "-q "
    chpw = " chapters "
    trks = " tracks "
    ffp_var1 = " -v error -hide_banner -show_format"
    ffp_var2 = " -show_entries stream_tags:format_tags"
    master = {"mkv": {}, "mp4": {}, "avi": {}, "dst": {}}
    re_se = re.compile(r"(.+)\.((s|S)(\d{1,2})(e|E)(\d{1,2}))")
    re_ext = re.compile(r".+\.(?:mp4|mkv|avi|m4v)$")
    re_del = re.compile(r".+\.(?:nfo|txt|rtf|jpg|bmp|url|htm|html|NFO)$")
    re_yr = re.compile(r"((.+)\.(\d{4}$))")
    re_yr2 = re.compile(r"(.+)( \(\d{4}\)$)")
    re_yr3 = re.compile(r"(.+)(\(\d{4}\)$)")
    #
    # other
    change_ele = 0

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
            cvars.change_ele = 1
            if ele_ment.endswith("/"):
                continue
            if str(ele_ment).endswith(".part"):
                continue
            f_Name = copy.deepcopy(ele_ment)
            f_change_needed = 0
            rename_list = open("rename_list.txt", "r", encoding="utf8")
            # match and rename Directories first
            f_Name = f_Name.replace(" ", ".")
            if re.match(r"^\/(.+)([\/])$", ele_ment):
                for rename_list_item in rename_list:
                    rename_item = rename_list_item.rstrip()
                    if rename_item in f_Name:
                        f_Name = f_Name.replace(rename_item, "")
                        os.rename(ele_ment, f_Name)
                        f_change_needed = 1
                        cvars.change_ele = 0
                    if f_change_needed == 1:
                        os.rename(ele_ment, f_Name)
                        cvars.change_ele = 0
                    else:
                        continue
            if not re.match(r".+\.(?:mp4|mkv|avi|m4v|mov|mpg)$", ele_ment):
                continue
            if os.path.exists(ele_ment):
                if cvars.change_ele == 1:
                    for rename_list_item in rename_list:
                        rename_item = rename_list_item.rstrip()
                        if rename_item in f_Name:
                            change_name = f_Name.replace(rename_item, "")
                            os.rename(ele_ment, change_name)
                            f_change_needed = 1
                        # if f_change_needed == 1:
                        #     os.rename(ele_ment, change_name)

    def check_comment(u):
        """return General track comment or description"""
        for Track in MediaInfo.parse(u).tracks:
            if not Track.track_type == "General":
                continue
            if Track.comment is not None:
                return Track.comment
            if Track.description is not None:
                return Track.description
            return Track.description

    def check_Gen_title(u):
        """return General track title"""
        for Track in MediaInfo.parse(u).tracks:
            if not Track.track_type == "General":
                continue
            else:
                return Track.title

    def check_Aud_title(u):
        """return Audio track title"""
        for Track in MediaInfo.parse(u).tracks:
            if not Track.track_type == "Audio":
                continue
            else:
                return Track.title

    def sbp_ret(x1x):
        """Run command and return output"""
        subprocess1 = subprocess.Popen(x1x, shell=True, stdout=subprocess.PIPE)
        subprocess_return1 = subprocess1.stdout.read()
        ret1 = subprocess_return1.decode("utf-8").split("\n")
        return ret1

    def sbp_run(x2x):
        """run command doesn't return output"""
        subprocess2 = subprocess.Popen(x2x, shell=True, stdout=subprocess.PIPE)
        subprocess_return2 = subprocess2.stdout.read()
        subprocess_return2

    def remove_space(file_list):
        for f in file_list:
            r = f.replace(" ", "")
            if r != f:
                os.rename(f, r)

    def remove_punc(file_list):
        punctuation = set(string.punctuation)
        punctuation.remove(".")
        punctuation.remove("-")
        punctuation.remove("/")
        for ele_ment in file_list:
            f_Name = str(ele_ment)
            for rename_item in punctuation:
                if ele_ment.endswith("/") or str(ele_ment).endswith(".part"):
                    continue
                f_Name = f_Name.replace(" ", ".")
                f_Name = f_Name.replace(rename_item, ".")
                f_Name = f_Name.replace("..", ".")
            if ele_ment != f_Name:
                os.rename(ele_ment, f_Name)


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"

    def disable(self):
        self.HEADER = ""
        self.OKBLUE = ""
        self.OKGREEN = ""
        self.WARNING = ""
        self.FAIL = ""
        self.ENDC = ""


# class c_mkv(clean):
#     def __init__(self):
#         self.mkv = {"mkv": {}}
#
#
# class c_mp4(clean):
#     def __init__(self):
#         self.mp4 = {"mp4": {}}
#
#
# class c_avi(clean):
#     def __init__(self):
#         self.avi = {"avi": {}}
#
#
# class c_dst(clean):
#     def __init__(self):
#         self.dst = {"dst": {}}
