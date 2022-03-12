from rename.fname_rename_l import fname_rename
from pymv.get_info import mkv_get_info
import os
import glob
import subprocess
import send2trash
from pathlib import Path
import re
import shutil

#

# ###### ERROR HANDLING!
# ##### Create a log file
# #### create better handling if there are multiple subtitle tracks
# ### Create better handling if there are multiple video tracks
# ## create better handling if there are multiple audio tracks
# # Maybe check chapters for info tracks, not sure what i meant now
# # maybe create settings file for global Vars
# # find a way to handle escape characters? []() and others
# # find a way to check that mp4/mkv is really that type container
# #     not just a renamed file extension
#
# # other ideas - Search: #?#

# start Adjustable Vars
#
# source folder to check (must end in slash)
ip = "/home/david/Downloads/jdownloader/"
# Destination folder to move and sort shows into (must end in slash)
destpath = "/media/Videos/Current-Renewed.Seasons/"
# temp folder to use (create if doesn't exist)
tmp11 = "/tmp/cleanvid/"
# Sub-title backup location
subpath = "/media/Videos/subs/"
#
# mkvtoolnix binary locations
mkv_info = "/usr/bin/mkvinfo "
mkv_e = "/usr/bin/mkvextract "
mkvmrg = "/usr/bin/mkvmerge "
# End Adjustable


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


# start global vars
slsh = "/"
mkmer = "-q --default-language 'eng' "
chpw = " chapters "
trks = " tracks "
ffp_var1 = " -v error -hide_banner -show_format"
ffp_var2 = " -show_entries stream_tags:format_tags"
ff_prob = "ffprobe" + ffp_var1 + ffp_var2
master = dict()
# create containers first for nested dict()
# if further nesting is needed,
# will need to declair it up front for easy append
# or until I understand nested dict better
master = {"mkv": {}, "mp4": {}, "dst": {}}
#
re_se = re.compile(r"(.+?)\.((s|S)(\d{1,2})(e|E)(\d{1,2}))")
re_ext = re.compile(r".+\.(?:mp4|mkv|avi|m4v)$")
re_yr = re.compile(r"((.+)\.(\d{4}$))")
# end global vars


def check_season(src_file, dst_folder, src_name, dst_name):
    sss = re_se.match(src_name)
    sea_list = glob.glob(dst_folder + "*" + slsh)
    dsm_chk = 0
    for dst_sea_lst in sea_list:
        dsl1 = dst_sea_lst.rstrip()
        dsl1 = dsl1.split(slsh)
        n1dsl = len(dsl1) - 2
        re_dst_sea = re.compile(r"(.*?)\w.(\d{1,2})")
        # split season so can match just number
        dsp1 = re_dst_sea.match(dsl1[n1dsl])
        if sss[4] == str(dsp1[2]):
            dsm_chk = 1
        else:
            continue
    if dsm_chk == 0:
        new_sea = dst_folder + "Season." + sss[4]
        os.mkdir(new_sea)
        print("Directory '% s' created" % new_sea)

    ex = 0
    ea = ""
    numa = 0
    eb = ""
    numb = 0
    ec = ""
    numc = 0
    for ext1 in src_name:
        ex = ex + 1
    numa = ex - 2
    numb = ex - 1
    numc = ex
    ex = 0
    for ext1 in src_name:
        ex = ex + 1
        if ex == numa:
            ea = ext1
        if ex == numb:
            eb = ext1
        if ex == numc:
            ec = ext1
    ext = "." + ea + eb + ec

    if ext == ".mkv":
        hd_ver, codec = mkv_get_info(src_file)
    elif ext == ".mp4":
        print("haven't written mp4")
        print("quitting for now! but get to it!")
        quit()
    else:
        print("Missing Container extension and process")

    mv_name = (
        dst_folder
        + "Season."
        + sss[4]
        + "/"
        + dst_name
        + ".S"
        + sss[4]
        + "E"
        + sss[6]
        + "."
        + codec
        + "."
        + hd_ver
        + ext
    )
    return mv_name


def sbp_ret(x1x):
    subprocess1 = subprocess.Popen(x1x, shell=True, stdout=subprocess.PIPE)
    subprocess_return1 = subprocess1.stdout.read()
    ret1 = subprocess_return1.decode("utf-8").split("\n")
    return ret1


def sbp_run(x2x):
    subprocess2 = subprocess.Popen(x2x, shell=True, stdout=subprocess.PIPE)
    subprocess_return2 = subprocess2.stdout.read()
    subprocess_return2


# check tmp folder
if not os.path.exists(tmp11):
    os.makedirs(tmp11)

# needed to strip escape characters and needless stuff in name
# rename folders first
fname_rename(glob.glob(ip + "*" + slsh))
# rename files next
fname_rename(glob.glob(ip + "**", recursive=True))

# ############################
# ####### Begin MKV ##########
# ############################
for path1 in Path(ip).rglob("*.mkv"):
    a = str(path1.expanduser()).split(path1.name)
    if a[0] is None:
        continue
    master["mkv"][path1.name] = {
        "change": "0",
        "chapters": "0",
        "videotr": "-1",
        "vtrnum": "a",
        "Vcodec": "0",
        "audiotr": "-1",
        "Acodec": "0",
        "subti": "0",
        # "dstPath": "0", # maybe add back later or useless now?
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
    }
    chk1 = re.match(r"(.+?)\.((s|S)(\d{1,2})(e|E)(\d{1,2}))", path1.name)
    if chk1 is None:
        master["mkv"][path1.name]["notshow"] = "1"
    nm = path1.name.split(".mkv")
    master["mkv"][path1.name]["name"] = nm[0]

# start master
# enter everything i'm looking for into Master from SRC folder
for aa1, bb1 in master["mkv"].items():
    cmd41 = mkv_info + ip + aa1
    for chap1 in sbp_ret(cmd41):
        if "Chapters" in chap1:
            master["mkv"][aa1]["chapters"] = "1"
        elif "Name:" in chap1:
            master["mkv"][aa1]["change"] = "1"
        elif "Title:" in chap1:
            master["mkv"][aa1]["change"] = "1"
    # video track and codec into master
    cmd42 = mkvmrg + "-i " + ip + aa1
    for vid2 in sbp_ret(cmd42):
        if "Track ID" in vid2:
            # double check RegEx
            vt = re.match(r"(Track ID )(\d): (video )\((.{3,4})\/.+", vid2)
            if vt is None:
                continue
            master["mkv"][aa1]["videotr"] = vt[2]
            master["mkv"][aa1]["Vcodec"] = vt[4]
            if int(master["mkv"][aa1]["videotr"]) > 0:
                master["mkv"][aa1]["change"] = "1"

    # audio track into master (default track is 1 if master is 0)
    for aud2 in sbp_ret(cmd42):
        if "subtitles" in aud2:
            master["mkv"][aa1]["subti"] = "1"
            master["mkv"][aa1]["change"] = "1"
        elif "Track ID" in aud2:
            at = re.match(r"(Track ID )(\d): (audio )\((.+)\)", aud2)
            if at is None:
                continue
            master["mkv"][aa1]["Acodec"] = at[4]
            master["mkv"][aa1]["audiotr"] = at[2]
# end master

# start update
# update name, season, episode in master
for aa2, bb2 in master["mkv"].items():
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
for aa3, bb3 in master["mkv"].items():
    if master["mkv"][aa3]["change"] == "1":
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
                print("broken in video extract")
                print("breaking on: ", aa3)
                break
            tr7d = mkv_e + ip + aa3 + trks + master["mkv"][aa3]["videotr"] + ":" + tr7f
            sbp_run(tr7d)
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
                    print("something is broken in Video Extract")
                    print("breaking while for file: ", aa3)
                    break
                tr7d = (
                    mkv_e + ip + aa3 + trks + master["mkv"][aa3]["videotr"] + ":" + tr7f
                )
                sbp_run(tr7d)
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
for aa9, bb9 in master["mkv"].items():
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
for aa4, bb4 in master["mkv"].items():
    if master["mkv"][aa4]["change"] == "1":
        aa4a = master["mkv"][aa4]["audiotr"]
        aa4b = master["mkv"][aa4]["Acodec"]
        aa4c = master["mkv"][aa4]["name"]
        aa4d = ".S" + master["mkv"][aa4]["sea"] + "E" + master["mkv"][aa4]["epi"]
        if master["mkv"][aa4]["notshow"] == "0":
            aa4e = tmp11 + aa4c + aa4d + "." + aa4b
        elif master["mkv"][aa4]["notshow"] == "1":
            aa4e = tmp11 + aa4c + "." + aa4b
        else:
            print("something broken in audio extract")
            print("breaking on: ", aa4)
            break
        aa4f = mkv_e + ip + aa4 + trks + aa4a + ":" + aa4e
        sbp_run(aa4f)
        master["mkv"][aa4]["taudio"] = aa4e
# end audio extract

# start chapter extract
for aa5, bb5 in master["mkv"].items():
    if master["mkv"][aa5]["change"] == "1":
        if master["mkv"][aa5]["chapters"] == "1":
            aa5a = master["mkv"][aa5]["name"]
            aa5f = master["mkv"][aa5]["sea"]
            aa5b = ".S" + aa5f + "E" + master["mkv"][aa5]["epi"]
            if master["mkv"][aa5]["notshow"] == "0":
                aa5c = tmp11 + aa5a + aa5b + ".xml"
            elif master["mkv"][aa5]["notshow"] == "1":
                aa5c = tmp11 + aa5a + ".xml"
            else:
                print("something broken in chapter extract")
                print("breaking on: ", aa5)
                break
            aa5d = mkv_e + ip + aa5 + chpw + aa5c
            sbp_run(aa5d)
            master["mkv"][aa5]["tchapters"] = aa5c
# end chapter extract

# start subtitle extract
for aa6, bb6 in master["mkv"].items():
    if master["mkv"][aa6]["subti"] == "1":
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
            print("broken - subtitle extract")
            print("breaking on: ", aa6)
            break
        aa6e = mkv_e + ip + aa6 + trks + aa6b + ":" + aa6d
        sbp_run(aa6e)
        master["mkv"][aa6]["tsubs"] = aa6d
# end subtitle extract

# #?# maybe increase size for deletion?
# #?# or find a better way to detect un-needed chapter exports
# start check/delete useless chapters
for aa7, bb7 in master["mkv"].items():
    # print(aa7)
    if master["mkv"][aa7]["tchapters"] != "0":
        if Path(master["mkv"][aa7]["tchapters"]).stat().st_size < 975:
            os.remove(master["mkv"][aa7]["tchapters"])
            master["mkv"][aa7]["tchapters"] = "0"
# end check/delete useless chapters
#
# start rebuilding MKVs
for aa8, bb8 in master["mkv"].items():
    if master["mkv"][aa8]["change"] == "1":
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
        print(bcolors.OKBLUE + "Recreating: " + bcolors.ENDC, aa8)
        sbp_run(aa8e)
        print(bcolors.OKBLUE + "deleting orig: " + bcolors.ENDC, aa8h)
        send2trash.send2trash(aa8h)
        print()
# end rebuilding MKVs

# start keep name tidy
fname_rename(glob.glob(ip + "**", recursive=True))
# end keep name tidy

# ################################
# #### begin checking MP4 ########
# ################################

for path2 in Path(ip).rglob("*.mp4"):
    master["mp4"][path2.name] = {
        "m4parent": "0",
        "m4title": "-1",
    }
    master["mp4"][path2.name]["m4parent"] = path2.parent

# check if mp4 has a title
for aa4, bb4 in master["mp4"].items():
    cmd30 = ff_prob + " " + str(master["mp4"][aa4]["m4parent"] / aa4)
    for mtitle in sbp_ret(cmd30):
        if "TAG:title=" not in mtitle:
            continue
        else:
            master["mp4"][aa4]["m4title"] = "1"

#
# #?# use ffmpeg instead of mkvmerge for converting mp4s
#
# do conversion of files in dictionary
for rm1, rm2 in master["mp4"].items():
    if master["mp4"][rm1]["m4title"] == "1":
        rmof = master["mp4"][rm1]["m4parent"] / rm1
        rm1a = rm1.split(".mp4")
        rm1b = rm1a[0] + ".mkv"
        rmcmd = mkvmrg + "-q --title '' -o " + ip + rm1b + " -S " + str(rmof)
        if os.path.exists(ip + rm1b):
            print(
                bcolors.WARNING + "Exists, why? Overwriting: " + bcolors.ENDC,
                rm1b,
            )
        print(bcolors.OKGREEN + "removing title from: " + bcolors.ENDC, rmof)
        sbp_run(rmcmd)
        print(bcolors.OKBLUE + "deleting orig: " + bcolors.ENDC, rmof)
        send2trash.send2trash(rmof)
        print()

fname_rename(glob.glob(ip + "**", recursive=True))

# #########################################
# Begin sorting process for move to NAS
# #########################################

dest_shows = dict()

dest_list = glob.glob(destpath + "*" + slsh)

for dst_lst in dest_list:
    dl1 = dst_lst.split(slsh)
    dest_shows[dl1[4]] = dst_lst

for path9 in Path(ip).rglob("*"):
    if re_ext.match(path9.name):
        if re_se.match(path9.name):
            x9 = re.match(r"(.*?)\.(S|s)(\d{1,2})(E|e)(\d{1,2})", path9.name)
            for k, v in dest_shows.items():
                if k.lower() == x9[1].lower():
                    master["dst"][path9] = check_season(path9, v, path9.name, k)
                    shutil.move(str(path9), str(master["dst"][path9]))
                    print("Moved: ", str(master["dst"][path9]))
                elif re_yr.match(x9[1]):
                    ww = re_yr.match(x9[1])
                    if k.lower() == ww[2].lower():
                        master["dst"][path9] = check_season(path9, v, path9.name, k)
                        shutil.move(str(path9), str(master["dst"][path9]))
                        print("Moved: ", str(master["dst"][path9]))
                elif re_yr.match(k):
                    # print("test")
                    ww = re_yr.match(k)
                    if x9[1].lower() == ww[2].lower():
                        master["dst"][path9] = check_season(path9, v, path9.name, k)
                        shutil.move(str(path9), str(master["dst"][path9]))
                        print("Moved: ", str(master["dst"][path9]))
                else:
                    continue
        # else:
        #     cmd50 = mkv_info + str(path9)
        #     for duration in sbp_ret(cmd50):
        #         if "Duration:" in duration:
        #             d50 = duration.split("Duration: ")
        #             d50 = tuple(d50[1].split(":"))
        #             print(d50)
        # master["mkv"][path9]["subti"] == 1:
        #     # mkv_get_info()
        #     print("yes")
#
# #?# maybe delete bogus subs?
# # #?# maybe keep same folder structure as DESTPATH?
for path4 in Path(tmp11).rglob("*.srt"):
    p4dst = str(path4).split(slsh)
    p4dst = subpath + p4dst[len(p4dst) - 1]
    mvsubs = shutil.move(str(path4), p4dst)
    print(bcolors.OKGREEN + "Moving sub: " + bcolors.ENDC, mvsubs)

for path5 in Path(tmp11).rglob("*"):
    if ".srt" in str(path5):
        continue
    os.remove(path5)
print(bcolors.OKBLUE + "Temp folder cleared" + bcolors.ENDC)

for path6 in Path(ip).rglob("*.htm"):
    os.remove(path6)
for path7 in Path(ip).rglob("*.txt"):
    os.remove(path7)
for path8 in Path(ip).rglob("*.nfo"):
    os.remove(path8)
print(bcolors.OKBLUE + "Junk files deleted" + bcolors.ENDC)

print("successfully finished, excluding unreported errors")
