import os
import re


def fname_rename(x):
    for y in x:
        if y.endswith("/"):
            continue
        if str(y).endswith(".part"):
            continue
        zz = y
        zr = "0"
        renlist = open("rename_list.txt", "r", encoding="utf8")
        # match and rename Directories first
        zz = zz.replace(" ", ".")
        if re.match(r"^\/(.+)([\/])$", y):
            for rl in renlist:
                rl1 = rl.rstrip()
                if rl1 in zz:
                    zz = zz.replace(rl1, ".")
                    zr = "1"
            if zr == "1":
                os.rename(y, zz)
                continue
        if not re.match(r".+\.(?:mp4|mkv|avi|m4v|mov|mpg)$", y):
            continue
        for rl in renlist:
            rl1 = rl.rstrip()
            if rl1 in zz:
                zz = zz.replace(rl1, ".")
                zr = "1"
        if zr == "1":
            os.rename(y, zz)
