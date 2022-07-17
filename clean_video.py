import os
import glob
import send2trash
from pathlib import Path
import re
import shutil
import xml.etree.ElementTree as ET
import logging
from pymediainfo import MediaInfo
import ctools


ctc = ctools.cvars

# Start Windows vs linux variables
if os.name == "nt":
    # Windows Settings
    slsh = ctc.win_slsh
    mkv_info = ctc.win_mkv_info
    mkv_e = ctc.win_mkv_e
    mkvmrg = ctc.win_mkvmrg
    mkvpedit = ctc.win_mkvpedit
    ff_mpg = ctc.win_ff_mpg
    ff_prob = ctc.win_ff_prob
    destpath = ctc.win_destpath
    ip = ctc.win_ip
    tmp11 = ctc.win_tmp11
    subpath = ctc.win_subpath
    logfile = ctc.win_logfile
else:
    # Linux settings
    slsh = ctc.nix_slsh
    mkv_info = ctc.nix_mkv_info
    mkv_e = ctc.nix_mkv_e
    mkvmrg = ctc.nix_mkvmrg
    mkvpedit = ctc.nix_mkvpedit
    ff_mpg = ctc.nix_ff_mpg
    ff_prob = ctc.nix_ff_prob
    destpath = ctc.nix_destpath_current
    # destpath = ctc.nix_destpath_ended
    subpath = ctc.nix_subpath
    logfile = ctc.nix_logfile
    # ramdisk setting not tested in Windows (keep to 0 for now)
    useramdsk = 0
    if useramdsk == 0:
        ip = ctc.nix_ip
        tmp11 = ctc.nix_tmp11
    elif useramdsk == 1:
        ip = ctc.nix_ramdisk_ip
        tmp11 = ctc.nix_ramdisk_tmp11
        trash11 = ctc.nix_ramdisk_trash11


# start global vars - Shouldn't need to change
ff_prob = ff_prob + ctc.ffp_var1 + ctc.ffp_var2
master = ctc.master
bcolors = ctools.bcolors()
# end global vars


logging.basicConfig(
    filename=logfile,
    format="%(asctime)s - %(message)s",
    datefmt="%y-%b-%d %H:%M:%S",
    level=logging.INFO,
)


def check_move_name(src_file, dst_folder, src_name, dst_name):
    """
    See if source file has a matching show in dest_path
    and then format the move name accordingly to return it
    """
    Season_epi_num = ctc.re_se.match(src_name)
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
    resolution, codec = ctools.clean.get_media_info(src_file)
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
        + resolution
        + src_file.suffix
    )
    return mv_name


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


def flatten_files(os_walk_path):
    for root, _, files1 in os_walk_path:
        for file1 in files1:
            path_file = os.path.join(root, file1)
            try:
                shutil.move(path_file, ip)
            except (shutil.SameFileError, shutil.Error):
                continue
        remove_empty_folders(ip)


ctools.clean.remove_punc(glob.glob(ip + "**", recursive=True))
ctools.clean.remove_space(glob.glob(ip + "**"))
flatten_files(os.walk(ip))
if not os.path.exists(tmp11):
    os.makedirs(tmp11)
ctools.clean.fname_rename(glob.glob(ip + "**", recursive=True))


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
for mkv_name1, _ in master["mkv"].items():
    Tstamp = os.stat(ip + mkv_name1)
    master["mkv"][mkv_name1]["st_atime"] = Tstamp.st_atime
    master["mkv"][mkv_name1]["st_mtime"] = Tstamp.st_mtime
    cmd41 = mkv_info + " " + ip + mkv_name1
    for chap1 in ctools.clean.sbp_ret(cmd41):
        if "Chapters" in chap1:
            master["mkv"][mkv_name1]["chapters"] = 1
        elif "Name:" in chap1:
            master["mkv"][mkv_name1]["change"] = 1
        elif "Title:" in chap1:
            master["mkv"][mkv_name1]["change"] = 1

# split complexity 1
print("Gathering info on files 3/5")
for mkv_name2, _ in master["mkv"].items():
    # video track and codec into master
    cmd42 = mkvmrg + " -i " + ip + mkv_name2
    for vid2 in ctools.clean.sbp_ret(cmd42):
        if "Track ID" in vid2:
            # double check RegEx
            vt = re.match(r"(Track ID )(\d): (video )\((.{3,4})\/.+", vid2)
            if vt is None:
                continue
            master["mkv"][mkv_name2]["videotr"] = vt[2]
            master["mkv"][mkv_name2]["Vcodec"] = vt[4]
            if int(master["mkv"][mkv_name2]["videotr"]) > 0:
                master["mkv"][mkv_name2]["change"] = 1
# split complexity 2
print("Gathering info on files 4/5")
for mkv_name3, _ in master["mkv"].items():
    cmd42 = mkvmrg + " -i " + ip + mkv_name3
    # audio track into master (default track is 1 if master is 0)
    for aud2 in ctools.clean.sbp_ret(cmd42):
        if "subtitles" in aud2:
            master["mkv"][mkv_name3]["subti"] = 1
            master["mkv"][mkv_name3]["change"] = 1
        elif "Track ID" in aud2:
            at = re.match(r"(Track ID )(\d): (audio )\((.+)\)", aud2)
            if at is None:
                continue
            # select first only (might need to change to look for title on trk)
            if master["mkv"][mkv_name3]["audiotr"] == "-1":
                master["mkv"][mkv_name3]["Acodec"] = at[4]
                master["mkv"][mkv_name3]["audiotr"] = at[2]
# check audio delay and set if needed
print("Gathering info on files 5/5\n")
for mkv_name4, _ in master["mkv"].items():
    for track in MediaInfo.parse(ip + mkv_name4).tracks:
        if track.track_type == "Audio":
            if track.delay_relative_to_video is not None:
                if track.delay_relative_to_video != "0":
                    # print(type(track.delay_relative_to_video))
                    master["mkv"][mkv_name4]["Adelay"] = int(
                        track.delay_relative_to_video
                    )
                    logging.debug("set Adelay")
                    logging.debug(mkv_name4)
                    logging.debug(type(master["mkv"][mkv_name4]["Adelay"]))
                    logging.debug(master["mkv"][mkv_name4]["Adelay"])
        else:
            continue
# end master

# begin remove tags
print("checking to remove tags")
for mkv_name5, _ in master["mkv"].items():
    fp_mkv_name5 = ip + mkv_name5
    if ctools.clean.check_comment(fp_mkv_name5) is not None:
        cmd43 = (
            mkvpedit
            + " "
            + str(fp_mkv_name5)
            + " --tags all: --add-track-statistics-tags"
        )
        logging.info(cmd43)
        print("remove tags in {}".format(mkv_name5))
        ctools.clean.sbp_run(cmd43)
        os.utime(
            fp_mkv_name5,
            (
                master["mkv"][mkv_name5]["st_atime"],
                master["mkv"][mkv_name5]["st_mtime"],
            ),
        )
# end remove tags

# start update
# update name, season, episode in master
print("splitting up Name, Season, Episode version in hashtable\n")
for mkv_name6, _ in master["mkv"].items():
    rn_nm = re.match(
        r"(.+?)\.((s|S)(\d{1,2})(e|E)(\d{1,2}))", master["mkv"][mkv_name6]["name"]
    )
    if rn_nm is None:
        continue
    master["mkv"][mkv_name6]["name"] = rn_nm[1]
    master["mkv"][mkv_name6]["sea"] = rn_nm[4]
    master["mkv"][mkv_name6]["epi"] = rn_nm[6]
# end update

# start video extract
print("Extracting Video tracks as needed")
for mkv_name7, _ in master["mkv"].items():
    if master["mkv"][mkv_name7]["change"] == 1:
        season_episode_num = (
            ".S"
            + master["mkv"][mkv_name7]["sea"]
            + "E"
            + master["mkv"][mkv_name7]["epi"]
        )
        if master["mkv"][mkv_name7]["videotr"] == "0":
            if master["mkv"][mkv_name7]["notshow"] == "0":
                name_minus_ext = (
                    tmp11
                    + master["mkv"][mkv_name7]["name"]
                    + season_episode_num
                    + "."
                    + master["mkv"][mkv_name7]["Vcodec"]
                )
            elif master["mkv"][mkv_name7]["notshow"] == "1":
                name_minus_ext = (
                    tmp11
                    + master["mkv"][mkv_name7]["name"]
                    + "."
                    + master["mkv"][mkv_name7]["Vcodec"]
                )
            else:
                logging.info("video extract failed on {}".format(mkv_name7))
                print("broken in video extract")
                print("breaking on: {}".format(mkv_name7))
                break
            mkv_v_extract_cmd = (
                mkv_e
                + " "
                + ip
                + mkv_name7
                + ctc.trks
                + master["mkv"][mkv_name7]["videotr"]
                + ":"
                + name_minus_ext
            )
            ctools.clean.sbp_run(mkv_v_extract_cmd)
            logging.info(mkv_v_extract_cmd)
            master["mkv"][mkv_name7]["tvideo"] = name_minus_ext
        elif int(master["mkv"][mkv_name7]["videotr"]) > 0:
            while int(master["mkv"][mkv_name7]["videotr"]) >= 0:
                if master["mkv"][mkv_name7]["notshow"] == "0":
                    name_minus_ext = (
                        tmp11
                        + master["mkv"][mkv_name7]["name"]
                        + season_episode_num
                        + "."
                        + master["mkv"][mkv_name7]["videotr"]
                        + "."
                        + master["mkv"][mkv_name7]["Vcodec"]
                    )
                elif master["mkv"][mkv_name7]["notshow"] == "1":
                    name_minus_ext = (
                        tmp11
                        + master["mkv"][mkv_name7]["name"]
                        + "."
                        + master["mkv"][mkv_name7]["videotr"]
                        + "."
                        + master["mkv"][mkv_name7]["Vcodec"]
                    )
                else:
                    logging.info("video extract failed on {}".format(mkv_name7))
                    print("something is broken in Video Extract")
                    print("breaking while for file: ", mkv_name7)
                    break
                mkv_v_extract_cmd = (
                    mkv_e
                    + " "
                    + ip
                    + mkv_name7
                    + ctc.trks
                    + master["mkv"][mkv_name7]["videotr"]
                    + ":"
                    + name_minus_ext
                )
                ctools.clean.sbp_run(mkv_v_extract_cmd)
                logging.info(mkv_v_extract_cmd)
                if master["mkv"][mkv_name7]["audiotr"] == "0":
                    master["mkv"][mkv_name7]["tvideo"] = name_minus_ext
                    tr7j = name_minus_ext.split(".")
                    master["mkv"][mkv_name7]["vtrnum"] = tr7j[len(tr7j) - 2]
                    break
                if master["mkv"][mkv_name7]["videotr"] == "0":
                    # ### find largest file of the group ###
                    #
                    # #?# could maybe check that smallers are actually small
                    # and hence not split video files
                    # also/or make a don't delete sub-tag in master
                    # to keep, if assumption wasn't correct
                    tr7h = filter(os.path.isfile, glob.glob(name_minus_ext + "*"))
                    tr7i = max_file = max(tr7h, key=lambda x: os.stat(x).st_size)
                    master["mkv"][mkv_name7]["tvideo"] = tr7i
                    tr7j = tr7i.split(".")
                    master["mkv"][mkv_name7]["vtrnum"] = tr7j[len(tr7j) - 2]
                    break
                master["mkv"][mkv_name7]["videotr"] = str(
                    int(master["mkv"][mkv_name7]["videotr"]) - 1
                )
# end video extract

# #?# Maybe different handling if I look into split tracks later (not seen yet)
# start set video track number if multiple tracks detected
print("updating video track info as needed")
for mkv_name8, _ in master["mkv"].items():
    if master["mkv"][mkv_name8]["vtrnum"] != "a":
        cmd41 = mkv_info + " " + ip + mkv_name8
        for c41_line in ctools.clean.sbp_ret(cmd41):
            Vtrack_num = str(int(master["mkv"][mkv_name8]["vtrnum"]) + 2)
            Vtrack_num = "Track number: " + Vtrack_num
            if Vtrack_num in c41_line:
                break
            elif "Horizontal chroma siting:" in c41_line:
                c41_lineb = c41_line.split("siting: ")
                master["mkv"][mkv_name8]["HchromaS"] = c41_lineb[1]
            elif "Vertical chroma siting:" in c41_line:
                c41_lineb = c41_line.split("siting: ")
                master["mkv"][mkv_name8]["VchromaS"] = c41_lineb[1]
# end set video track

# #?# Might have to add handling of multiple audio tracks to strip languages
# start audio extract
print("extracting Audio track as needed\n")
for mkv_name9, _ in master["mkv"].items():
    if master["mkv"][mkv_name9]["change"] == 1:
        aud_tr9 = master["mkv"][mkv_name9]["audiotr"]
        aud_cdc9 = master["mkv"][mkv_name9]["Acodec"]
        str_name9 = master["mkv"][mkv_name9]["name"]
        season_epi_num9 = (
            ".S"
            + master["mkv"][mkv_name9]["sea"]
            + "E"
            + master["mkv"][mkv_name9]["epi"]
        )
        if master["mkv"][mkv_name9]["notshow"] == "0":
            aa4e = tmp11 + str_name9 + season_epi_num9 + "." + aud_cdc9
        elif master["mkv"][mkv_name9]["notshow"] == "1":
            aa4e = tmp11 + str_name9 + "." + aud_cdc9
        else:
            logging.info("broke on {}".format(mkv_name9))
            print("something broken in audio extract")
            print("breaking on: ", mkv_name9)
            break
        aud_extract_cmd = mkv_e + " " + ip + mkv_name9 + ctc.trks + aud_tr9 + ":" + aa4e
        ctools.clean.sbp_run(aud_extract_cmd)
        logging.info(aud_extract_cmd)
        master["mkv"][mkv_name9]["taudio"] = aa4e
# end audio extract

# start chapter extract
print("chapter extract as needed")
for mkv_name10, _ in master["mkv"].items():
    if master["mkv"][mkv_name10]["change"] == 1:
        if master["mkv"][mkv_name10]["chapters"] == 1:
            str_name10 = master["mkv"][mkv_name10]["name"]
            Season_num10 = master["mkv"][mkv_name10]["sea"]
            Season_epi_str10 = (
                ".S" + Season_num10 + "E" + master["mkv"][mkv_name10]["epi"]
            )
            if master["mkv"][mkv_name10]["notshow"] == "0":
                aa5c = tmp11 + str_name10 + Season_epi_str10 + ".xml"
            elif master["mkv"][mkv_name10]["notshow"] == "1":
                aa5c = tmp11 + str_name10 + ".xml"
            else:
                logging.info("broke on {}".format(mkv_name10))
                print("something broken in chapter extract")
                print("breaking on: ", mkv_name10)
                break
            chptr_extrct_cmd10 = mkv_e + " " + ip + mkv_name10 + ctc.chpw + aa5c
            ctools.clean.sbp_run(chptr_extrct_cmd10)
            logging.info(chptr_extrct_cmd10)
            master["mkv"][mkv_name10]["tchapters"] = aa5c
# end chapter extract

# start subtitle extract
print("subtitle extract as needed")
for mkv_name11, _ in master["mkv"].items():
    if master["mkv"][mkv_name11]["subti"] == 1:
        str_name11 = master["mkv"][mkv_name11]["name"]
        if master["mkv"][mkv_name11]["audiotr"] == "0":
            sub_trck_num11 = "2"
        else:
            sub_trck_num11 = str(int(master["mkv"][mkv_name11]["audiotr"]) + 1)
        season_num11 = master["mkv"][mkv_name11]["sea"]
        seasn_epi_str11 = ".S" + season_num11 + "E" + master["mkv"][mkv_name11]["epi"]
        if master["mkv"][mkv_name11]["notshow"] == "0":
            extrcted_sub_name11 = tmp11 + str_name11 + seasn_epi_str11 + ".srt"
        elif master["mkv"][mkv_name11]["notshow"] == "1":
            extrcted_sub_name11 = tmp11 + str_name11 + ".srt"
        else:
            logging.info("broke on {}".format(mkv_name11))
            print("broken - subtitle extract")
            print("breaking on: ", mkv_name11)
            break
        extrcted_sub_cmd11 = (
            mkv_e
            + " "
            + ip
            + mkv_name11
            + ctc.trks
            + sub_trck_num11
            + ":"
            + extrcted_sub_name11
        )
        ctools.clean.sbp_run(extrcted_sub_cmd11)
        logging.info(extrcted_sub_cmd11)
        master["mkv"][mkv_name11]["tsubs"] = extrcted_sub_name11
# end subtitle extract

# #?# maybe increase size for deletion?
# #?# or find a better way to detect un-needed chapter exports
# start check/delete useless chapters
print("removing junk chapters")
for mkv_name12, _ in master["mkv"].items():
    # print(mkv_name12)
    if master["mkv"][mkv_name12]["tchapters"] != "0":
        if Path(master["mkv"][mkv_name12]["tchapters"]).stat().st_size < 975:
            logging.info("removing {}".format(master["mkv"][mkv_name12]["tchapters"]))
            os.remove(master["mkv"][mkv_name12]["tchapters"])
            master["mkv"][mkv_name12]["tchapters"] = "0"
# end check/delete useless chapters

# Begin chapter word replace
print("Chapter word replace if needed\n")
for mkv_name13, _ in master["mkv"].items():
    if master["mkv"][mkv_name13]["tchapters"] != "0":
        xmlTree = ET.parse(master["mkv"][mkv_name13]["tchapters"])
        rootElement = xmlTree.getroot()
        for element in rootElement.findall("EditionEntry"):
            for element2 in element.findall("ChapterAtom"):
                for element3 in element2.findall("ChapterDisplay"):
                    if element3.find("ChapterString").text.startswith("CapÃ­tulo"):
                        rpl = element3.find("ChapterString").text.split(" ")
                        element3.find("ChapterString").text = "Chapter " + rpl[1]
        xmlTree.write(
            master["mkv"][mkv_name13]["tchapters"],
            encoding="UTF-8",
            xml_declaration=True,
        )
# end chapter word replace

# start rebuilding MKVs
print("rebuilding MKVs if tracks were extracted")
for mkv_name14, _ in master["mkv"].items():
    if master["mkv"][mkv_name14]["change"] == 1:
        if master["mkv"][mkv_name14]["tchapters"] != "0":
            partial_14c = master["mkv"][mkv_name14]["tchapters"]
            partial_14d = "--clusters-in-meta-seek -S --chapters " + partial_14c
        else:
            partial_14d = "--clusters-in-meta-seek -S"
        if (
            master["mkv"][mkv_name14]["HchromaS"]
            and master["mkv"][mkv_name14]["VchromaS"] != "a"
        ):
            hchromas_num14 = master["mkv"][mkv_name14]["HchromaS"]
            vchromas_num14 = master["mkv"][mkv_name14]["VchromaS"]
            partial_14d = (
                partial_14d
                + " --chroma-subsample 0:"
                + hchromas_num14
                + ","
                + vchromas_num14
            )
        if master["mkv"][mkv_name14]["notshow"] == "0":
            season_epi_num14 = (
                master["mkv"][mkv_name14]["name"]
                + ".S"
                + master["mkv"][mkv_name14]["sea"]
                + "E"
                + master["mkv"][mkv_name14]["epi"]
                + "."
                + master["mkv"][mkv_name14]["Vcodec"]
            )
        elif master["mkv"][mkv_name14]["notshow"] == "1":
            season_epi_num14 = master["mkv"][mkv_name14]["name"]
        if master["mkv"][mkv_name14]["Adelay"] != 0:
            rebuild_cmd14 = (
                mkvmrg
                + " "
                + ctc.mkmer
                + partial_14d
                + " "
                + master["mkv"][mkv_name14]["tvideo"]
                + " --sync -1:"
                + str(master["mkv"][mkv_name14]["Adelay"])
                + " "
                + master["mkv"][mkv_name14]["taudio"]
                + " -o "
                + ip
                + season_epi_num14
                + "-CHANGED-"
                + ".mkv"
            )
        else:
            rebuild_cmd14 = (
                mkvmrg
                + " "
                + ctc.mkmer
                + partial_14d
                + " "
                + master["mkv"][mkv_name14]["tvideo"]
                + " "
                + master["mkv"][mkv_name14]["taudio"]
                + " -o "
                + ip
                + season_epi_num14
                + "-CHANGED-"
                + ".mkv"
            )
        file_to_delete14 = ip + mkv_name14
        print(bcolors.OKGREEN + "Recreating: " + bcolors.ENDC, mkv_name14)
        # print(rebuild_cmd14)
        ctools.clean.sbp_run(rebuild_cmd14)
        logging.info(rebuild_cmd14)
        print(bcolors.OKBLUE + "deleting orig: " + bcolors.ENDC, file_to_delete14)
        path14 = os.path.join(ip, mkv_name14)
        # print("path: ", path14)
        # quit()
        if useramdsk == 0:
            send2trash.send2trash(path14)
        elif useramdsk == 1:
            shutil.move(file_to_delete14, trash11 + mkv_name14)
        logging.info("sending to trash {}".format(path14))
        print()
        new_file_name14 = os.path.join(ip, (season_epi_num14 + "-CHANGED-.mkv"))
        # print(new_file_name14)
        os.utime(
            new_file_name14,
            (
                master["mkv"][mkv_name14]["st_atime"],
                master["mkv"][mkv_name14]["st_mtime"],
            ),
        )
        # quit()
# end rebuilding MKVs

# start keep name tidy
ctools.clean.fname_rename(glob.glob(ip + "**", recursive=True))
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
for mp4_name1, _ in master["mp4"].items():
    Tstamp = os.stat(ip + mp4_name1)
    master["mp4"][mp4_name1]["m4st_atime"] = Tstamp.st_atime
    master["mp4"][mp4_name1]["m4st_mtime"] = Tstamp.st_mtime
    cmd30 = ff_prob + " " + str(master["mp4"][mp4_name1]["m4parent"] / mp4_name1)
    for mtitle in ctools.clean.sbp_ret(cmd30):
        if "TAG:title=" in mtitle:
            master["mp4"][mp4_name1]["m4title"] = "1"
        elif "TAG:comment=" in mtitle:
            master["mp4"][mp4_name1]["m4comment"] = 1
        else:
            continue

# do conversion of files in dictionary
print("Converting MP4 to mkv")
for mp4_name2, _ in master["mp4"].items():
    if (
        master["mp4"][mp4_name2]["m4title"] == "1"
        or master["mp4"][mp4_name2]["m4comment"] == 1
    ):
        fpath = master["mp4"][mp4_name2]["m4parent"] / mp4_name2
        fpath_mkv = str(fpath.stem) + ".mkv"
        rmcmd = (
            mkvmrg
            + " -q --clusters-in-meta-seek --title '' -o "
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
        ctools.clean.sbp_run(rmcmd)
        logging.info(rmcmd)
        print(bcolors.OKBLUE + "deleting orig: " + bcolors.ENDC, fpath)

        cmd32 = mkvpedit + " " + ip + fpath_mkv + " --edit track:v1 --set name=''"
        ctools.clean.sbp_run(cmd32)
        print("edit video track name on {}".format(fpath_mkv))
        logging.info(cmd32)
        # cmd33 = mkvpedit + " " + ip + fpath_mkv + " --edit track:a1 --set name=''"
        # ctools.clean.sbp_run(cmd33)
        # print("edit audio track name on {}".format(fpath_mkv))
        # logging.info(cmd33)
        if useramdsk == 0:
            send2trash.send2trash(fpath)
        elif useramdsk == 1:
            log2 = str(fpath) + " " + str(trash11) + str(mp4_name2)
            logging.info(log2)
            shutil.move(fpath, trash11 + mp4_name2)
        os.utime(
            ip + fpath_mkv,
            (
                master["mp4"][mp4_name2]["m4st_atime"],
                master["mp4"][mp4_name2]["m4st_mtime"],
            ),
        )
        logging.info("trashing {}".format(fpath))
        print()

ctools.clean.fname_rename(glob.glob(ip + "**", recursive=True))
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
        ctools.clean.check_Gen_title(fileAvi)
        or ctools.clean.check_Aud_title(fileAvi)
        or ctools.clean.check_comment(fileAvi) is not None
    ):
        master["avi"][fAname]["avititle"] = 2

print("converting AVI if needed")
for avi_name, avi_values in master["avi"].items():
    atmpname = (
        ip
        + master["avi"][avi_name]["aviStem"]
        + "-CHANGED-"
        + master["avi"][avi_name]["aviExt"]
    )
    # print(atmpname)
    if avi_values["avititle"] > 1:
        avi_convert_cmd = (
            ff_mpg
            + " -fflags +genpts -i "
            + ip
            + avi_name
            + " -map_metadata -1 -c:v copy -c:a copy "
            + "-fflags +bitexact -flags:v +bitexact -flags:a +bitexact "
            + atmpname
        )
        ctools.clean.sbp_run(avi_convert_cmd)
    if useramdsk == 0:
        send2trash.send2trash(ip + avi_name)
    elif useramdsk == 1:
        log2 = ip + avi_name + " " + str(trash11) + avi_name
        logging.info(log2)
        shutil.move(ip + avi_name, trash11 + avi_name)
    os.utime(
        atmpname,
        (
            master["avi"][avi_name]["avist_atime"],
            master["avi"][avi_name]["avist_mtime"],
        ),
    )

ctools.clean.fname_rename(glob.glob(ip + "**", recursive=True))

# end AVI check/remove title

# #########################################
# Begin sorting process for move to NAS
# #########################################
print("\nStarting move to destination\n")
dest_shows = dict()

dest_list = glob.glob(destpath + "*" + slsh)

for dlist in dest_list:
    dl_split = dlist.split(slsh)
    dest_shows[dl_split[len(dl_split) - 2]] = dlist

# print("dest shows: ", dest_shows)
for path9 in Path(ip).rglob("*"):
    # print("p9: ", path9)
    if str(path9).endswith(".part"):
        continue
    if ctc.re_ext.match(path9.name):
        if ctc.re_se.match(path9.name):
            x9 = re.match(r"(.*?)\.(S|s)(\d{1,2})(E|e)(\d{1,2})", path9.name)
            # print("x9: ", x9)
            for k, v in dest_shows.items():
                # print("k", k)
                # print(x9[1].lower())
                if k.lower() == x9[1].lower():
                    master["dst"][path9] = check_move_name(path9, v, path9.name, k)
                    shutil.move(str(path9), str(master["dst"][path9]))
                    logging.info("moved to {}".format(str(master["dst"][path9])))
                    print(
                        bcolors.OKBLUE + "Moved: " + bcolors.ENDC,
                        str(master["dst"][path9]),
                    )
                elif ctc.re_yr.match(x9[1]):
                    ww = ctc.re_yr.match(x9[1])
                    if k.lower() == ww[2].lower():
                        master["dst"][path9] = check_move_name(path9, v, path9.name, k)
                        shutil.move(str(path9), master["dst"][path9])
                        logging.info("moved to {}".format(str(master["dst"][path9])))
                        print(
                            bcolors.OKBLUE + "Moved: " + bcolors.ENDC,
                            str(master["dst"][path9]),
                        )
                elif ctc.re_yr.match(k):
                    # print("test")
                    ww = ctc.re_yr.match(k)
                    if x9[1].lower() == ww[2].lower():
                        master["dst"][path9] = check_move_name(path9, v, path9.name, k)
                        shutil.move(str(path9), master["dst"][path9])
                        logging.info("moved to {}".format(str(master["dst"][path9])))
                        print(
                            bcolors.OKBLUE + "Moved: " + bcolors.ENDC,
                            str(master["dst"][path9]),
                        )
                elif ctc.re_yr2.match(k):
                    ww = ctc.re_yr2.match(k)
                    # print(k)
                    # print("ww: {}".format(ww))
                    if ww[1].lower() == x9[1].lower():
                        master["dst"][path9] = check_move_name(path9, v, path9.name, k)
                        shutil.move(str(path9), master["dst"][path9])
                        logging.info("moved to {}".format(master["dst"][path9]))
                        print(
                            bcolors.OKBLUE + "moved: " + bcolors.ENDC,
                            str(master["dst"][path9]),
                        )
                elif ctc.re_yr3.match(k):
                    ww = ctc.re_yr3.match(k)
                    # print(path9)
                    if ww[1].lower() == x9[1].lower():
                        master["dst"][path9] = check_move_name(path9, v, path9.name, k)
                        shutil.move(str(path9), str(master["dst"][path9]))
                        logging.info("moved to {}".format(master["dst"][path9]))
                        print(
                            bcolors.OKBLUE + "moved: " + bcolors.ENDC,
                            str(master["dst"][path9]),
                        )

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
    if ctc.re_del.match(str(junkfile)):
        os.remove(junkfile)
    else:
        continue
print(bcolors.OKBLUE + "junk files deleted" + bcolors.ENDC)
print("successfully finished, excluding unreported errors")
