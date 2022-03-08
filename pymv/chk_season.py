import re
import glob
import os
from pymv.get_info import mkv_get_info

# need_rn = 0
re_se = re.compile(r"(.*?)((S)(\d{1,2}))((E)(\d{1,2}))")
# re_yr = re.compile(r"((.+)\.(\d+$))")


def check_season(src_file, dst_folder, src_name, dst_name):
    sss = re.match(r"(.*?)\.(S|s)(\d{1,2})(E|e)(\d{1,2})", src_name)
    sea_list = glob.glob(dst_folder + "*/")
    dsm_chk = 0
    for dst_sea_lst in sea_list:
        dsl1 = dst_sea_lst.rstrip()
        dsl1 = dsl1.split("/")
        n1dsl = len(dsl1) - 2
        re_dst_sea = re.compile(r"(.*?)\w.(\d{1,2})")
        # split season so can match just number
        dsp1 = re_dst_sea.match(dsl1[n1dsl])
        if sss[3] == str(dsp1[2]):
            dsm_chk = 1
        else:
            continue
    if dsm_chk == 0:
        new_sea = dst_folder + "Season." + sss[3]
        os.mkdir(new_sea)
        print("Directory '% s' created" % new_sea)
        # print("didn't match season number, created it")

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
        + sss[3]
        + "/"
        + dst_name
        + ".S"
        + sss[3]
        + "E"
        + sss[5]
        + "."
        + hd_ver
        + "."
        + codec
        + ext
    )

    return mv_name
