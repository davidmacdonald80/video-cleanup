from rename.fname_rename_l import fname_rename
from pymv.get_info import get_media_info
import os
import glob
import subprocess
import send2trash
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import logging
from pymediainfo import MediaInfo

# from pymv.get_info import mkv_get_info
# from pymv.get_info import mp4_get_info
# from pymv.get_info import avi_get_info

# Start Windows vs linux variables
if os.name == "nt":
    # Windows Settings
    # don't change slsh line
    slsh = "\\"
    # Change if you didn't use default path
    # Leave the at the end + " "
    mkv_info = '"c:\\Program Files\\MKVToolNix\\mkvinfo.exe"' + " "
    mkv_e = '"c:\\Program Files\\MKVToolNix\\mkvextract.exe"' + " "
    mkvmrg = '"c:\\Program Files\\MKVToolNix\\mkvmerge.exe"' + " "
    mkvpedit = '"c:\\Program Files\\MKVToolNix\\mkvpropedit.exe"' + " "
    # update the path if needed but leave the space -hide_banner space '
    ff_mpg = '"c:\\portables\\ffmpeg\\bin\\ffmpeg.exe" -hide_banner '
    # update path if needed - no space on this one
    ff_prob = "c:\\portables\\ffmpeg\\bin\\ffprobe.exe"
else:
    # Linux settings
    # don't change the slsh line
    slsh = "/"
    # update the path if needed - Leave trailing space
    mkv_info = "/usr/bin/mkvinfo "
    mkv_e = "/usr/bin/mkvextract "
    mkvmrg = "/usr/bin/mkvmerge "
    mkvpedit = "/usr/bin/mkvpropedit "
    # update if needed
    ff_mpg = "/usr/bin/ffmpeg -hide_banner "
    ff_prob = "/usr/bin/ffprobe"

# start path variables
#
# Windows use \\
# Linux use /
#
# destpath = "c:\\destp\\dst\\"
# ip = "c:\\srcpath\\Downloads\\" # set in useramdsk 0 setting
# tmp11 = "c:\\tmp\\cleanvid\\" # set in useramdsk 0 setting
# subpath = "c:\\destp\\sbs\\"
# logfile = "c:\\srcpath\\clean-move.log"
#
destpath = "/media/Videos/Current-Renewed.Seasons/"
# destpath = "/media/Videos/Ended-Cancelled.Seasons/"
subpath = "/media/Videos/subs/"
logfile = "/home/david/Downloads/clean-move.log"
#
# ramdisk setting not tested in Windows (keep to 0 for now)
useramdsk = 1
# source folder to check (must end in slash) and temp folder
if useramdsk == 0:
    ip = "/home/david/Downloads/jdownloader/"
    tmp11 = "/tmp/cleanvid/"
elif useramdsk == 1:
    ip = "/tmp/ramdisk/clean/"
    tmp11 = "/tmp/ramdisk/tmp/"
    trash11 = "/tmp/ramdisk/trash/"
else:
    print("incorrect ramdisk setting, quitting")
    quit()

# end path variables
# end Windows vs linux


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


logging.basicConfig(
    filename=logfile,
    format="%(asctime)s - %(message)s",
    datefmt="%y-%b-%d %H:%M:%S",
    level=logging.INFO,
)

# start global vars - Shouldn't need to change
# mkmer = "-q --default-language 'eng' "
mkmer = "-q "
chpw = " chapters "
trks = " tracks "
ffp_var1 = " -v error -hide_banner -show_format"
ffp_var2 = " -show_entries stream_tags:format_tags"
ff_prob = ff_prob + ffp_var1 + ffp_var2
master = dict()
master = {"mkv": {}, "mp4": {}, "avi": {}, "dst": {}}
re_se = re.compile(r"(.+)\.((s|S)(\d{1,2})(e|E)(\d{1,2}))")
re_ext = re.compile(r".+\.(?:mp4|mkv|avi|m4v)$")
re_del = re.compile(r".+\.(?:nfo|txt|rtf|jpg|bmp|url|htm|html|NFO)$")
re_yr = re.compile(r"((.+)\.(\d{4}$))")
re_yr2 = re.compile(r"(.+)( \(\d{4}\)$)")
re_yr3 = re.compile(r"(.+)(\(\d{4}\)$)")
# end global vars


def check_season(src_file, dst_folder, src_name, dst_name):
    Season_epi_num = re_se.match(src_name)
    dest_folder_chk = 0
    for dst_sea_lst in glob.glob(dst_folder + "*" + slsh):
        path_split = dst_sea_lst.rstrip().split(slsh)
        re_dst_sea = re.compile(r"(.*?)\w.(\d{1,2})")
        dst_season_num = re_dst_sea.match(path_split[len(path_split) - 2])
        if dst_season_num is None:
            continue
        if Season_epi_num[4] == str(dst_season_num[2]):
            dest_folder_chk = 1
        else:
            continue
    if dest_folder_chk == 0:
        new_season_folder = dst_folder + "Season." + Season_epi_num[4]
        os.mkdir(new_season_folder)
        print(
            bcolors.OKGREEN
            + "Directory created "
            + bcolors.ENDC
            + "{}".format(new_season_folder)
        )
    hd_ver, codec = get_media_info(src_file)
    mv_name = (
        dst_folder
        + "Season."
        + Season_epi_num[4]
        + slsh
        + dst_name
        + ".S"
        + Season_epi_num[4]
        + "E"
        + Season_epi_num[6]
        + "."
        + codec
        + "."
        + hd_ver
        + src_file.suffix
    )
    return mv_name


def check_comment(u):
    for Track in MediaInfo.parse(u).tracks:
        if not Track.track_type == "General":
            continue
        if Track.comment is not None:
            return Track.comment
        if Track.description is not None:
            return Track.description
        return Track.description


def check_Gen_title(u):
    for Track in MediaInfo.parse(u).tracks:
        if not Track.track_type == "General":
            continue
        else:
            return Track.title


def check_Aud_title(u):
    for Track in MediaInfo.parse(u).tracks:
        if not Track.track_type == "Audio":
            continue
        else:
            return Track.title


def sbp_ret(x1x):
    subprocess1 = subprocess.Popen(x1x, shell=True, stdout=subprocess.PIPE)
    subprocess_return1 = subprocess1.stdout.read()
    ret1 = subprocess_return1.decode("utf-8").split("\n")
    return ret1


def sbp_run(x2x):
    subprocess2 = subprocess.Popen(x2x, shell=True, stdout=subprocess.PIPE)
    subprocess_return2 = subprocess2.stdout.read()
    subprocess_return2


def remove_empty_folders(path_abs):
    walk = list(os.walk(path_abs))
    for (
        path11,
        _,
        _,
    ) in walk[::-1]:
        if len(os.listdir(path11)) == 0:
            if path11 != ip:
                os.rmdir(path11)
            else:
                continue


# remove spaces from filenames
for f in glob.glob(ip + "**"):
    r = f.replace(" ", "")
    if r != f:
        os.rename(f, r)

# check tmp folder
if not os.path.exists(tmp11):
    os.makedirs(tmp11)

# flatten files
for root, _, files1 in os.walk(ip):
    for file1 in files1:
        path_file = os.path.join(root, file1)
        try:
            shutil.move(path_file, ip)
        except (shutil.SameFileError, shutil.Error):
            continue
    remove_empty_folders(ip)

# rename folders first
# fname_rename(glob.glob(ip + "*" + slsh))
# rename files next
fname_rename(glob.glob(ip + "**", recursive=True))

# ############################
# ####### Begin MKV ##########
# ############################
print("Gathering info on files 1/5")
for path1 in Path(ip).rglob("*.mkv"):
    a = str(path1.expanduser()).split(path1.name)
    if a[0] is None:
        continue
    master["mkv"][path1.name] = {
        "change": 0,
        "chapters": 0,
        "videotr": "-1",
        "vtrnum": "a",
        "Vcodec": "0",
        "audiotr": "-1",
        "Acodec": "0",
        "subti": 0,
        "Adelay": 0,
        "name": "0",
        "sea": "0",
        "epi": "0",
        "HchromaS": "a",
        "VchromaS": "a",
        "notshow": "0",
        "tvideo": "0",
        "taudio": "0",
        "tchapters": "0",
        "tsubs": "0",
        "st_atime": "-1",
        "st_mtime": "-1",
    }
    chk1 = re.match(r"(.+?)\.((s|S)(\d{1,2})(e|E)(\d{1,2}))", path1.name)
    if chk1 is None:
        master["mkv"][path1.name]["notshow"] = "1"
    nm = path1.name.split(".mkv")
    master["mkv"][path1.name]["name"] = nm[0]

# start master
# enter everything i'm looking for into Master from SRC folder
print("Gathering info on files 2/5")
for aa1, _ in master["mkv"].items():
    Tstamp = os.stat(ip + aa1)
    master["mkv"][aa1]["st_atime"] = Tstamp.st_atime
    master["mkv"][aa1]["st_mtime"] = Tstamp.st_mtime
    cmd41 = mkv_info + ip + aa1
    for chap1 in sbp_ret(cmd41):
        if "Chapters" in chap1:
            master["mkv"][aa1]["chapters"] = 1
        elif "Name:" in chap1:
            master["mkv"][aa1]["change"] = 1
        elif "Title:" in chap1:
            master["mkv"][aa1]["change"] = 1

# split complexity 1
print("Gathering info on files 3/5")
for ac1, _ in master["mkv"].items():
    # video track and codec into master
    cmd42 = mkvmrg + "-i " + ip + ac1
    for vid2 in sbp_ret(cmd42):
        if "Track ID" in vid2:
            # double check RegEx
            vt = re.match(r"(Track ID )(\d): (video )\((.{3,4})\/.+", vid2)
            if vt is None:
                continue
            master["mkv"][ac1]["videotr"] = vt[2]
            master["mkv"][ac1]["Vcodec"] = vt[4]
            if int(master["mkv"][ac1]["videotr"]) > 0:
                master["mkv"][ac1]["change"] = 1
# split complexity 2
print("Gathering info on files 4/5")
for ac2, _ in master["mkv"].items():
    cmd42 = mkvmrg + "-i " + ip + ac2
    # audio track into master (default track is 1 if master is 0)
    for aud2 in sbp_ret(cmd42):
        if "subtitles" in aud2:
            master["mkv"][ac2]["subti"] = 1
            master["mkv"][ac2]["change"] = 1
        elif "Track ID" in aud2:
            at = re.match(r"(Track ID )(\d): (audio )\((.+)\)", aud2)
            if at is None:
                continue
            # select first only (might need to change to look for title on trk)
            if master["mkv"][ac2]["audiotr"] == "-1":
                master["mkv"][ac2]["Acodec"] = at[4]
                master["mkv"][ac2]["audiotr"] = at[2]
# check audio delay and set if needed
print("Gathering info on files 5/5\n")
for ac3, _ in master["mkv"].items():
    for track in MediaInfo.parse(ip + ac3).tracks:
        if track.track_type == "Audio":
            if track.delay_relative_to_video is not None:
                if track.delay_relative_to_video != "0":
                    # print(type(track.delay_relative_to_video))
                    master["mkv"][ac3]["Adelay"] = int(track.delay_relative_to_video)
                    logging.debug("set Adelay")
                    logging.debug(ac3)
                    logging.debug(type(master["mkv"][ac3]["Adelay"]))
                    logging.debug(master["mkv"][ac3]["Adelay"])
        else:
            continue
# end master

# begin remove tags
print("checking to remove tags")
for ac5, _ in master["mkv"].items():
    fac5 = ip + ac5
    if check_comment(fac5) is not None:
        cmd43 = mkvpedit + str(fac5) + " --tags all: --add-track-statistics-tags"
        logging.info(cmd43)
        print("remove tags in {}".format(ac5))
        sbp_run(cmd43)
        os.utime(fac5, (master["mkv"][ac5]["st_atime"], master["mkv"][ac5]["st_mtime"]))
# end remove tags

# start update
# update name, season, episode in master
print("splitting up Name, Season, Episode version in hashtable\n")
for aa2, _ in master["mkv"].items():
    rn_nm = re.match(
        r"(.+?)\.((s|S)(\d{1,2})(e|E)(\d{1,2}))", master["mkv"][aa2]["name"]
    )
    if rn_nm is None:
        continue
    master["mkv"][aa2]["name"] = rn_nm[1]
    master["mkv"][aa2]["sea"] = rn_nm[4]
    master["mkv"][aa2]["epi"] = rn_nm[6]
# end update

# start video extract
print("Extracting Video tracks as needed")
for aa3, _ in master["mkv"].items():
    if master["mkv"][aa3]["change"] == 1:
        tr7e = ".S" + master["mkv"][aa3]["sea"] + "E" + master["mkv"][aa3]["epi"]
        if master["mkv"][aa3]["videotr"] == "0":
            if master["mkv"][aa3]["notshow"] == "0":
                tr7f = (
                    tmp11
                    + master["mkv"][aa3]["name"]
                    + tr7e
                    + "."
                    + master["mkv"][aa3]["Vcodec"]
                )
            elif master["mkv"][aa3]["notshow"] == "1":
                tr7f = (
                    tmp11
                    + master["mkv"][aa3]["name"]
                    + "."
                    + master["mkv"][aa3]["Vcodec"]
                )
            else:
                logging.info("video extract failed on {}".format(aa3))
                print("broken in video extract")
                print("breaking on: {}".format(aa3))
                break
            tr7d = mkv_e + ip + aa3 + trks + master["mkv"][aa3]["videotr"] + ":" + tr7f
            sbp_run(tr7d)
            logging.info(tr7d)
            master["mkv"][aa3]["tvideo"] = tr7f
        elif int(master["mkv"][aa3]["videotr"]) > 0:
            while int(master["mkv"][aa3]["videotr"]) >= 0:
                if master["mkv"][aa3]["notshow"] == "0":
                    tr7f = (
                        tmp11
                        + master["mkv"][aa3]["name"]
                        + tr7e
                        + "."
                        + master["mkv"][aa3]["videotr"]
                        + "."
                        + master["mkv"][aa3]["Vcodec"]
                    )
                elif master["mkv"][aa3]["notshow"] == "1":
                    tr7f = (
                        tmp11
                        + master["mkv"][aa3]["name"]
                        + "."
                        + master["mkv"][aa3]["videotr"]
                        + "."
                        + master["mkv"][aa3]["Vcodec"]
                    )
                else:
                    logging.info("video extract failed on {}".format(aa3))
                    print("something is broken in Video Extract")
                    print("breaking while for file: ", aa3)
                    break
                tr7d = (
                    mkv_e + ip + aa3 + trks + master["mkv"][aa3]["videotr"] + ":" + tr7f
                )
                sbp_run(tr7d)
                logging.info(tr7d)
                if master["mkv"][aa3]["audiotr"] == "0":
                    master["mkv"][aa3]["tvideo"] = tr7f
                    tr7j = tr7f.split(".")
                    master["mkv"][aa3]["vtrnum"] = tr7j[len(tr7j) - 2]
                    break
                if master["mkv"][aa3]["videotr"] == "0":
                    # ### find largest file of the group ###
                    #
                    # #?# could maybe check that smallers are actually small
                    # and hence not split video files
                    # also/or make a don't delete sub-tag in master
                    # to keep, if assumption wasn't correct
                    tr7h = filter(os.path.isfile, glob.glob(tr7f + "*"))
                    tr7i = max_file = max(tr7h, key=lambda x: os.stat(x).st_size)
                    master["mkv"][aa3]["tvideo"] = tr7i
                    tr7j = tr7i.split(".")
                    master["mkv"][aa3]["vtrnum"] = tr7j[len(tr7j) - 2]
                    break
                master["mkv"][aa3]["videotr"] = str(
                    int(master["mkv"][aa3]["videotr"]) - 1
                )
# end video extract

# #?# Maybe different handling if I look into split tracks later (not seen yet)
# start set video track number if multiple tracks detected
print("updating video track info as needed")
for aa9, _ in master["mkv"].items():
    if master["mkv"][aa9]["vtrnum"] != "a":
        cmd41 = mkv_info + ip + aa9
        for trnum1 in sbp_ret(cmd41):
            trnum1a = str(int(master["mkv"][aa9]["vtrnum"]) + 2)
            trnum1a = "Track number: " + trnum1a
            if trnum1a in trnum1:
                break
            elif "Horizontal chroma siting:" in trnum1:
                trnum1b = trnum1.split("siting: ")
                master["mkv"][aa9]["HchromaS"] = trnum1b[1]
            elif "Vertical chroma siting:" in trnum1:
                trnum1b = trnum1.split("siting: ")
                master["mkv"][aa9]["VchromaS"] = trnum1b[1]
# end set video track

# #?# Might have to add handling of multiple audio tracks to strip languages
# start audio extract
print("extracting Audio track as needed\n")
for aa4, _ in master["mkv"].items():
    if master["mkv"][aa4]["change"] == 1:
        aa4a = master["mkv"][aa4]["audiotr"]
        aa4b = master["mkv"][aa4]["Acodec"]
        aa4c = master["mkv"][aa4]["name"]
        aa4d = ".S" + master["mkv"][aa4]["sea"] + "E" + master["mkv"][aa4]["epi"]
        if master["mkv"][aa4]["notshow"] == "0":
            aa4e = tmp11 + aa4c + aa4d + "." + aa4b
        elif master["mkv"][aa4]["notshow"] == "1":
            aa4e = tmp11 + aa4c + "." + aa4b
        else:
            logging.info("broke on {}".format(aa4))
            print("something broken in audio extract")
            print("breaking on: ", aa4)
            break
        aa4f = mkv_e + ip + aa4 + trks + aa4a + ":" + aa4e
        sbp_run(aa4f)
        logging.info(aa4f)
        master["mkv"][aa4]["taudio"] = aa4e
# end audio extract

# start chapter extract
print("chapter extract as needed")
for aa5, _ in master["mkv"].items():
    if master["mkv"][aa5]["change"] == 1:
        if master["mkv"][aa5]["chapters"] == 1:
            aa5a = master["mkv"][aa5]["name"]
            aa5f = master["mkv"][aa5]["sea"]
            aa5b = ".S" + aa5f + "E" + master["mkv"][aa5]["epi"]
            if master["mkv"][aa5]["notshow"] == "0":
                aa5c = tmp11 + aa5a + aa5b + ".xml"
            elif master["mkv"][aa5]["notshow"] == "1":
                aa5c = tmp11 + aa5a + ".xml"
            else:
                logging.info("broke on {}".format(aa5))
                print("something broken in chapter extract")
                print("breaking on: ", aa5)
                break
            aa5d = mkv_e + ip + aa5 + chpw + aa5c
            sbp_run(aa5d)
            logging.info(aa5d)
            master["mkv"][aa5]["tchapters"] = aa5c
# end chapter extract

# start subtitle extract
print("subtitle extract as needed")
for aa6, _ in master["mkv"].items():
    if master["mkv"][aa6]["subti"] == 1:
        aa6a = master["mkv"][aa6]["name"]
        if master["mkv"][aa6]["audiotr"] == "0":
            aa6b = "2"
        else:
            aa6b = str(int(master["mkv"][aa6]["audiotr"]) + 1)
        aa6z = master["mkv"][aa6]["sea"]
        aa6c = ".S" + aa6z + "E" + master["mkv"][aa6]["epi"]
        if master["mkv"][aa6]["notshow"] == "0":
            aa6d = tmp11 + aa6a + aa6c + ".srt"
        elif master["mkv"][aa6]["notshow"] == "1":
            aa6d = tmp11 + aa6a + ".srt"
        else:
            logging.info("broke on {}".format(aa6))
            print("broken - subtitle extract")
            print("breaking on: ", aa6)
            break
        aa6e = mkv_e + ip + aa6 + trks + aa6b + ":" + aa6d
        sbp_run(aa6e)
        logging.info(aa6e)
        master["mkv"][aa6]["tsubs"] = aa6d
# end subtitle extract

# #?# maybe increase size for deletion?
# #?# or find a better way to detect un-needed chapter exports
# start check/delete useless chapters
print("removing junk chapters")
for aa7, _ in master["mkv"].items():
    # print(aa7)
    if master["mkv"][aa7]["tchapters"] != "0":
        if Path(master["mkv"][aa7]["tchapters"]).stat().st_size < 975:
            logging.info("removing {}".format(master["mkv"][aa7]["tchapters"]))
            os.remove(master["mkv"][aa7]["tchapters"])
            master["mkv"][aa7]["tchapters"] = "0"
# end check/delete useless chapters

# Begin chapter word replace
print("Chapter word replace if needed\n")
for ab1, _ in master["mkv"].items():
    if master["mkv"][aa7]["tchapters"] != "0":
        xmlTree = ET.parse(master["mkv"][aa7]["tchapters"])
        rootElement = xmlTree.getroot()
        for element in rootElement.findall("EditionEntry"):
            for element2 in element.findall("ChapterAtom"):
                for element3 in element2.findall("ChapterDisplay"):
                    if element3.find("ChapterString").text.startswith("CapÃ­tulo"):
                        rpl = element3.find("ChapterString").text.split(" ")
                        element3.find("ChapterString").text = "Chapter " + rpl[1]
        xmlTree.write(
            master["mkv"][aa7]["tchapters"], encoding="UTF-8", xml_declaration=True
        )
# end chapter word replace

# start rebuilding MKVs
print("rebuilding MKVs if tracks were extracted")
for aa8, _ in master["mkv"].items():
    if master["mkv"][aa8]["change"] == 1:
        if master["mkv"][aa8]["tchapters"] != "0":
            aa8c = master["mkv"][aa8]["tchapters"]
            aa8d = "--clusters-in-meta-seek -S --chapters " + aa8c
        else:
            aa8d = "--clusters-in-meta-seek -S"
        if master["mkv"][aa8]["HchromaS"] and master["mkv"][aa1]["VchromaS"] != "a":
            aa8f = master["mkv"][aa8]["HchromaS"]
            aa8g = master["mkv"][aa8]["VchromaS"]
            aa8d = aa8d + " --chroma-subsample 0:" + aa8f + "," + aa8g
        if master["mkv"][aa8]["notshow"] == "0":
            aa8a = (
                master["mkv"][aa8]["name"]
                + ".S"
                + master["mkv"][aa8]["sea"]
                + "E"
                + master["mkv"][aa8]["epi"]
                + "."
                + master["mkv"][aa8]["Vcodec"]
            )
        elif master["mkv"][aa8]["notshow"] == "1":
            aa8a = master["mkv"][aa8]["name"]
        if master["mkv"][ac3]["Adelay"] != 0:
            aa8e = (
                mkvmrg
                + mkmer
                + aa8d
                + " "
                + master["mkv"][aa8]["tvideo"]
                + " --sync -1:"
                + str(master["mkv"][aa8]["Adelay"])
                + " "
                + master["mkv"][aa8]["taudio"]
                + " -o "
                + ip
                + aa8a
                + "-CHANGED-"
                + ".mkv"
            )
        else:
            aa8e = (
                mkvmrg
                + mkmer
                + aa8d
                + " "
                + master["mkv"][aa8]["tvideo"]
                + " "
                + master["mkv"][aa8]["taudio"]
                + " -o "
                + ip
                + aa8a
                + "-CHANGED-"
                + ".mkv"
            )
        aa8h = ip + aa8
        print(bcolors.OKGREEN + "Recreating: " + bcolors.ENDC, aa8)
        # print(aa8e)
        sbp_run(aa8e)
        logging.info(aa8e)
        print(bcolors.OKBLUE + "deleting orig: " + bcolors.ENDC, aa8h)
        path99 = os.path.join(ip, aa8)
        # print("path: ", path99)
        # quit()
        if useramdsk == 0:
            send2trash.send2trash(path99)
        elif useramdsk == 1:
            shutil.move(aa8h, trash11 + aa8)
        logging.info("sending to trash {}".format(path99))
        print()
        aa8aa = os.path.join(ip, (aa8a + "-CHANGED-.mkv"))
        # print(aa8aa)
        os.utime(
            aa8aa, (master["mkv"][aa8]["st_atime"], master["mkv"][aa8]["st_mtime"])
        )
        # quit()
# end rebuilding MKVs

# start keep name tidy
fname_rename(glob.glob(ip + "**", recursive=True))
# end keep name tidy

# ################################
# #### begin checking MP4 ########
# ################################
print("gather info on MP4 as needed")
for path2 in Path(ip).rglob("*.mp4"):
    master["mp4"][path2.name] = {
        "m4parent": "0",
        "m4title": "-1",
        "m4comment": -1,
        "m4st_atime": "-1",
        "m4st_mtime": "-1",
        # "m4Vtrack": "-1",
        # "m4Atrack": "-1",
    }
    master["mp4"][path2.name]["m4parent"] = path2.parent

for path2 in Path(ip).rglob("*.m4v"):
    master["mp4"][path2.name] = {
        "m4parent": "0",
        "m4title": "-1",
        "m4comment": 0,
        "m4st_atime": "-1",
        "m4st_mtime": "-1",
        # "m4Vtrack": "-1",
        # "m4Atrack": "-1",
    }
    master["mp4"][path2.name]["m4parent"] = path2.parent

# check if mp4 has a title/comment
for aa4, _ in master["mp4"].items():
    Tstamp = os.stat(ip + aa4)
    master["mp4"][aa4]["m4st_atime"] = Tstamp.st_atime
    master["mp4"][aa4]["m4st_mtime"] = Tstamp.st_mtime
    cmd30 = ff_prob + " " + str(master["mp4"][aa4]["m4parent"] / aa4)
    for mtitle in sbp_ret(cmd30):
        if "TAG:title=" in mtitle:
            master["mp4"][aa4]["m4title"] = "1"
        elif "TAG:comment=" in mtitle:
            master["mp4"][aa4]["m4comment"] = 1
        else:
            continue

# do conversion of files in dictionary
print("Converting MP4 to mkv")
for rm1, _ in master["mp4"].items():
    if master["mp4"][rm1]["m4title"] == "1" or master["mp4"][rm1]["m4comment"] == 1:
        fpath = master["mp4"][rm1]["m4parent"] / rm1
        fpath_mkv = str(fpath.stem) + ".mkv"
        rmcmd = (
            mkvmrg
            + "-q --clusters-in-meta-seek --title '' -o "
            + ip
            + fpath_mkv
            + " -S "
            + str(fpath)
        )
        # print(rmcmd)
        if os.path.exists(ip + fpath_mkv):
            print(
                bcolors.WARNING + "Exists, why? Overwriting: " + bcolors.ENDC,
                fpath_mkv,
            )
        print(bcolors.OKGREEN + "removing title from: " + bcolors.ENDC, fpath)
        sbp_run(rmcmd)
        logging.info(rmcmd)
        print(bcolors.OKBLUE + "deleting orig: " + bcolors.ENDC, fpath)
        # mkvpropedit Fname.S06E01.x264.mkv --edit track:v1 --set name="" track:a1 --set name=""
        cmd32 = mkvpedit + ip + fpath_mkv + " --edit track:v1 --set name=''"
        sbp_run(cmd32)
        print("edit video track name on {}".format(fpath_mkv))
        logging.info(cmd32)
        cmd33 = mkvpedit + ip + fpath_mkv + " --edit track:a1 --set name=''"
        sbp_run(cmd33)
        print("edit audio track name on {}".format(fpath_mkv))
        logging.info(cmd33)
        if useramdsk == 0:
            send2trash.send2trash(fpath)
        elif useramdsk == 1:
            log2 = str(fpath) + " " + str(trash11) + str(rm1)
            logging.info(log2)
            shutil.move(fpath, trash11 + rm1)
        os.utime(
            ip + fpath_mkv,
            (master["mp4"][aa4]["m4st_atime"], master["mp4"][aa4]["m4st_mtime"]),
        )
        logging.info("trashing {}".format(fpath))
        print()

fname_rename(glob.glob(ip + "**", recursive=True))
# End MP4

# #####################################
# ### Begin AVI check/remove title
# #####################################
print("gathering info on AVI as needed")
for fileAvi in Path(ip).rglob("*.avi"):
    fAname = fileAvi.name
    master["avi"][fAname] = {
        "aviStem": "1",
        "aviparent": "0",
        "avititle": -1,
        "avist_atime": "-1",
        "avist_mtime": "-1",
        "aviExt": "1",
        "aviComment": 0,
    }
    master["avi"][fAname]["aviparent"] = fileAvi.parent
    master["avi"][fAname]["aviStem"] = fileAvi.stem
    Tstamp = os.stat(str(fileAvi))
    master["avi"][fAname]["avist_atime"] = Tstamp.st_atime
    master["avi"][fAname]["avist_mtime"] = Tstamp.st_mtime
    master["avi"][fAname]["aviExt"] = fileAvi.suffix
    if (
        check_Gen_title(fileAvi)
        or check_Aud_title(fileAvi)
        or check_comment(fileAvi) is not None
    ):
        master["avi"][fAname]["avititle"] = 2

print("converting AVI if needed")
for rm3, rm4 in master["avi"].items():
    atmpname = (
        ip + master["avi"][rm3]["aviStem"] + "-CHANGED-" + master["avi"][rm3]["aviExt"]
    )
    if rm4["avititle"] > 1:
        avi_convert_cmd = (
            ff_mpg
            + "-fflags +genpts "
            + "-i "
            + ip
            + rm3
            + " -map_metadata -1 -c:v copy -c:a copy "
            + "-fflags +bitexact -flags:v +bitexact -flags:a +bitexact "
            + atmpname
        )
        sbp_run(avi_convert_cmd)
    if useramdsk == 0:
        send2trash.send2trash(ip + rm3)
    elif useramdsk == 1:
        log2 = ip + rm3 + " " + str(trash11) + rm3
        logging.info(log2)
        shutil.move(ip + rm3, trash11 + rm3)
    os.utime(
        atmpname,
        (master["avi"][rm3]["avist_atime"], master["avi"][rm3]["avist_mtime"]),
    )

fname_rename(glob.glob(ip + "**", recursive=True))

# end AVI check/remove title

# #########################################
# Begin sorting process for move to NAS
# #########################################
print("\nStarting move to destination\n")
dest_shows = dict()

dest_list = glob.glob(destpath + "*" + slsh)

for dst_lst in dest_list:
    dl1 = dst_lst.split(slsh)
    dest_shows[dl1[len(dl1) - 2]] = dst_lst

# print("dest shows: ", dest_shows)
for path9 in Path(ip).rglob("*"):
    # print("p9: ", path9)
    if str(path9).endswith(".part"):
        continue
    if re_ext.match(path9.name):
        if re_se.match(path9.name):
            x9 = re.match(r"(.*?)\.(S|s)(\d{1,2})(E|e)(\d{1,2})", path9.name)
            # print("x9: ", x9)
            for k, v in dest_shows.items():
                # print("k", k)
                # print(x9[1].lower())
                if k.lower() == x9[1].lower():
                    master["dst"][path9] = check_season(path9, v, path9.name, k)
                    shutil.move(str(path9), str(master["dst"][path9]))
                    logging.info("moved to {}".format(str(master["dst"][path9])))
                    print(
                        bcolors.OKBLUE + "Moved: " + bcolors.ENDC,
                        str(master["dst"][path9]),
                    )
                elif re_yr.match(x9[1]):
                    ww = re_yr.match(x9[1])
                    if k.lower() == ww[2].lower():
                        master["dst"][path9] = check_season(path9, v, path9.name, k)
                        shutil.move(str(path9), master["dst"][path9])
                        logging.info("moved to {}".format(str(master["dst"][path9])))
                        print(
                            bcolors.OKBLUE + "Moved: " + bcolors.ENDC,
                            str(master["dst"][path9]),
                        )
                elif re_yr.match(k):
                    # print("test")
                    ww = re_yr.match(k)
                    if x9[1].lower() == ww[2].lower():
                        master["dst"][path9] = check_season(path9, v, path9.name, k)
                        shutil.move(str(path9), master["dst"][path9])
                        logging.info("moved to {}".format(str(master["dst"][path9])))
                        print(
                            bcolors.OKBLUE + "Moved: " + bcolors.ENDC,
                            str(master["dst"][path9]),
                        )
                elif re_yr2.match(k):
                    ww = re_yr2.match(k)
                    # print(k)
                    # print("ww: {}".format(ww))
                    if ww[1].lower() == x9[1].lower():
                        master["dst"][path9] = check_season(path9, v, path9.name, k)
                        shutil.move(str(path9), master["dst"][path9])
                        logging.info("moved to {}".format(master["dst"][path9]))
                        print(
                            bcolors.OKBLUE + "moved: " + bcolors.ENDC,
                            str(master["dst"][path9]),
                        )
                elif re_yr3.match(k):
                    ww = re_yr3.match(k)
                    # print(path9)
                    if ww[1].lower() == x9[1].lower():
                        master["dst"][path9] = check_season(path9, v, path9.name, k)
                        shutil.move(str(path9), str(master["dst"][path9]))
                        logging.info("moved to {}".format(master["dst"][path9]))
                        print(
                            bcolors.OKBLUE + "moved: " + bcolors.ENDC,
                            str(master["dst"][path9]),
                        )
                else:
                    # print(k)
                    continue
#
# # #?# maybe keep same folder structure as DESTPATH?
for path4 in Path(tmp11).rglob("*.srt"):
    p4dst = str(path4).split(slsh)
    p4dst = subpath + p4dst[len(p4dst) - 1]
    if Path(path4).stat().st_size < 990:
        os.remove(path4)
    else:
        mvsubs = shutil.move(str(path4), p4dst)
        logging.info("moved sub to {}".format(p4dst))
        print(bcolors.OKGREEN + "Moving sub: " + bcolors.ENDC, mvsubs)

for path5 in Path(tmp11).rglob("*"):
    if ".srt" in str(path5):
        continue
    if useramdsk == 0:
        send2trash.send2trash(path5)
    elif useramdsk == 1:
        log1 = "Move: " + str(path5) + " " + trash11 + str(path5.name)
        logging.info(log1)
        shutil.move(str(path5), trash11 + str(path5.name))
print(bcolors.OKBLUE + "Temp folder cleared" + bcolors.ENDC)

for junkfile in Path(ip).rglob("*"):
    if re_del.match(str(junkfile)):
        os.remove(junkfile)
    else:
        continue
print(bcolors.OKBLUE + "junk files deleted" + bcolors.ENDC)
print("successfully finished, excluding unreported errors")
