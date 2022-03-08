import os
import re


def fname_rename(x):
    for y in x:
        zz = y
        zr = "0"
        # match and rename Directories first
        if re.match(r"^\/(.+)([\/])$", y):
            if "'" in zz:
                zz = zz.translate(str.maketrans({"'": None}))
                zr = "1"
            renlist = open("rename_list.txt", "r")
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
        # do this check first because not sure how else
        # to check for single quote in rename list.
        # Might have to add other escape characters later
        if "'" in zz:
            zz = zz.translate(str.maketrans({"'": None}))
            zr = "1"
        renlist = open("rename_list.txt", "r")
        for rl in renlist:
            rl1 = rl.rstrip()
            if rl1 in zz:
                zz = zz.replace(rl1, ".")
                zr = "1"
        if zr == "1":
            os.rename(y, zz)
