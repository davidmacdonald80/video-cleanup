from rename.fname_rename_l import fname_rename
from mv.chk_season import check_season
import os
import glob
import subprocess
import send2trash
from pathlib import Path
import re
import shutil

#

# #### create better handling if there are multiple subtitle tracks
# ### Create better handling if there are multiple video tracks
# ## create better handling if there are multiple audio tracks
# # Maybe check chapters for info tracks?
# # maybe use Var in .split("/") for easy transition to Windows?
# # maybe create settings file for global Vars
# # find a way to handle escape characters? []() and others
#
# # other ideas - Search: # #?#


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


# source folder to check
ip = "/home/david/Downloads/jdownloader/"
# Destination folder to move and sort shows into
destpath = "/media/Videos/Current-Renewed.Seasons/"
# temp folder to use (create if doesn't exist)
tmp11 = "/tmp/cleanvid/"
# Sub-title backup location
subpath = "/media/Videos/subs/"

# start global vars
mkv_info = "/usr/bin/mkvinfo "
mkv_e = "/usr/bin/mkvextract "
mkvmrg = "/usr/bin/mkvmerge "
mkmer = "/usr/bin/mkvmerge -q --default-language 'eng' "
chpw = " chapters "
trks = " tracks "
ffp_var1 = " -v error -hide_banner -show_format"
ffp_var2 = " -show_entries stream_tags:format_tags"
ff_prob = "ffprobe" + ffp_var1 + ffp_var2

has_title = dict()
mp4has_title = dict()
mp4_title = dict()

master = dict()
# create containers first for nested dict()
# if further nesting is needed,
# will need to declair it up front for easy append
# or until I understand nested dict better
master = {"mkv": {}, "mp4": {}, "avi": {}, "m4v": {}}
# end global vars


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
fname_rename(glob.glob(ip + "*/"))
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
        # #?# could put continue to not process
        # maybe add setting here for later?
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
        vid1 = 0
        cdc = ""
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
    if master["mkv"][aa7]["tchapters"] != "0":
        if Path(master["mkv"][aa7]["tchapters"]).stat().st_size < 975:
            os.remove(master["mkv"][aa7]["tchapters"])
            master["mkv"][aa7]["tchapters"] = "0"
# end check/delete useless chapters

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
            aa8a = master["mkv"][aa8]["name"] + "." + master["mkv"][aa8]["Vcodec"]
        aa8e = (
            mkmer
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
        sbp_run(aa8e)
        print(bcolors.OKBLUE + "deleting orig: " + bcolors.ENDC, aa8h)
        send2trash.send2trash(aa8h)
# end rebuilding MKVs

# start keep name tidy
fname_rename(glob.glob(ip + "**", recursive=True))
# end keep name tidy

# ################################
# #### begin checking MP4 ########
# ################################

# test - probably keep and build from
for path2 in Path(ip).rglob("*.mp4"):
    a = str(path2.expanduser()).split(path2.name)
    if a[0] is None:
        continue
    master["mp4"][path2.name] = {
        "something": "0",
        "something": "-1",
        "something": "a",
        "something": "0",
        "something": "-1",
        "something": "0",
    }

#
# edit or re-write to use master["mp4"]
#
for path3 in Path(ip).rglob("*.mp4"):
    a4 = str(path3.expanduser()).split(path3.name)
    if a4 is None:
        continue
    mp4_title[path3.name] = a4[0]

# check if mp4 has a title
for aa4, bb4 in mp4_title.items():
    cmd30 = ff_prob + " " + bb4 + aa4
    for mtitle in sbp_ret(cmd30):
        if "TAG:title=" not in mtitle:
            continue
        else:
            mp4has_title[aa4] = bb4

# do conversion of files in dictionary
for rm1, rm2 in mp4has_title.items():
    rmof = rm2 + rm1
    rm1n = os.path.splitext(rm1)
    mkv_nm = rm2 + rm1n[0] + ".mkv"
    rmcmd = mkvmrg + "-q -o " + mkv_nm + " -S " + rmof
    if os.path.exists(mkv_nm):
        print(
            bcolors.WARNING + "Exists, why? Overwriting: " + bcolors.ENDC,
            mkv_nm,
        )
    print(bcolors.OKGREEN + "removing title from: " + bcolors.ENDC, rmof)
    sbp_run(rmcmd)
    print(bcolors.OKBLUE + "deleting orig: " + bcolors.ENDC, rmof)
    send2trash.send2trash(rmof)

fname_rename(glob.glob(ip + "**", recursive=True))


# #########################################
# Begin sorting process for move to NAS
# #########################################

# Most likely re-write everything here for sing dict()
# still a lot to do before this

# dest_shows = dict()

# dest_list = glob.glob(destpath + "*/")

# for cur_list in dest_list:
#     cl1 = cur_list.split("/")
#     dest_shows[cl1[4]] = cur_list

re_ext = re.compile(r".+\.(?:mp4|mkv|avi|m4v)$")
re_se = re.compile(r"(.+?)\.((s|S)(\d{1,2})(e|E)(\d{1,2}))")
re_yr = re.compile(r"((.+)\.(\d+$))")
mv_name = dict()

# don't delete below til re-write!

for path9 in Path(ip).rglob("*"):
    str_path9 = str(path9)
    if re_ext.match(path9.name):
        if re_se.match(path9.name):
            x9 = re.match(r"(.*?)\.(S|s)(\d{1,2})(E|e)(\d{1,2})", path9.name)
            # for k, v in dest_shows.items():
            #     if k.lower() == x9[1].lower():
            #         mv_name[path9] = check_season(path9, v, path9.name, k)
            #     elif re.match(r"((.+)\.(\d+$))", x9[1]):
            #         ww = re.match(r"((.+?)\.(\d+$))", x9[1])
            #         if k.lower() == ww[2].lower():
            #             mv_name[path9] = check_season(path9, v, path9.name, k)
            #     elif re_yr.match(k):
            #         ww = re.match(r"((.+)\.(\d+$))", k)
            #         if x9[1].lower() == ww[2].lower():
            #             mv_name[path9] = check_season(path9, v, path9.name, k)
            # else:
            #     continue


#
# #?# maybe delete bogus subs?
# #?# maybe keep same folder structure as DESTPATH?
for path4 in Path(tmp11).rglob("*.srt"):
    p4dst = str(path4).split("/")
    p4dst = subpath + p4dst[len(p4dst) - 1]
    # mvsubs = shutil.move(str(path4), p4dst)
    # print(mvsubs)

    # disabled at work

for path5 in Path(tmp11).rglob("*"):
    if ".srt" in str(path5):
        continue
    os.remove(path5)

# another safeguard check, probably need more as this probably doesn't work
# if not bool(mv_name):
#     # print("mv_name: ", mv_name)
#     # print("nothing prcessed, quitting")
#     quit()


# print("mv_name: ", mv_name)

# print("last: ", master["mkv"])

print("successfully finished, excluding unreported errors")
