import os
import re


def fname_rename(x):
    for y in x:
        zz = y
        zr = "0"
        renlist = open("rename_list.txt", "r")
        # match and rename Directories first
        if re.match(r"^\/(.+)([\/])$", y):
            if "'" in zz:
                zz = zz.translate(str.maketrans({"'": None}))
                zr = "1"
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
        if "'" in zz:
            zz = zz.translate(str.maketrans({"'": None}))
            zr = "1"
        for rl in renlist:
            rl1 = rl.rstrip()
            if rl1 in zz:
                zz = zz.replace(rl1, ".")
                zr = "1"
        if zr == "1":
            os.rename(y, zz)
