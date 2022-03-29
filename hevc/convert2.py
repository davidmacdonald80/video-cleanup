from subprocess import PIPE
from ffprobe import FFProbe
from pathlib import Path
import multiprocessing
import time
import os
import signal
import subprocess
import shlex
import psutil
import send2trash
import logging

ip = "/home/david/Downloads/jdownloader/"
fmpg0 = "/usr/bin/ffmpeg "
fmpg1 = " -hide_banner -hwaccel auto -i "  # insert src + 2
fmpg2 = (
    " -movflags faststart"
    + " -c:v hevc_nvenc -n -rc 1"
    + " -rc-lookahead 20 -no-scenecut 0 -cq 32 -c:a "
)
logfile = "/home/david/Downloads/convert.log"
logging.basicConfig(
    filename=logfile,
    format="%(asctime)s - %(message)s",
    datefmt="%y-%b-%d %H:%M:%S",
    level=logging.INFO,
)
# multiprocessing idea from:
# http://net-informations.com/python/pro/sleep.htm

# pulled nvidia_smi commands needed from GPUtil code
#   Could update for windows based on that code
# pip install gputil # (don't think you need to install at this point)
# https://github.com/anderskm/gputil
#


def getTemp():
    nvidia_smi = "/usr/bin/nvidia-smi"
    gpucmd = subprocess.Popen(
        [nvidia_smi, "--query-gpu=temperature.gpu", "--format=csv,noheader,nounits"],
        stdout=PIPE,
    )
    stdout, stderr = gpucmd.communicate()
    Temp = stdout.decode("UTF-8").rstrip()
    return Temp


def probe_file_codec(filename):
    cmnd = "ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1"
    cmnd = cmnd + " " + str(filename)
    cmnd = shlex.split(cmnd)
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = out.rstrip()
    out = str(out).strip("b'")
    out = out.replace("'", "")
    return out


def probe_duration(filename):
    cmnd = "ffprobe -v error -select_streams v:0 -show_entries format=duration -of default=noprint_wrappers=1:nokey=1"
    cmnd = cmnd + " " + str(filename)
    cmnd = shlex.split(cmnd)
    p = subprocess.Popen(cmnd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    out = out.rstrip()
    out = str(out).strip("b'")
    out = out.replace("'", "")
    if "." in out:
        out = out.split(".")
        return out[0]
    else:
        return out


# return audio codec
def Acdc(srcvid):
    for stream in FFProbe(srcvid).streams:
        if stream.is_audio():
            return stream.codec_name


def convert2hevc(srcvid, parent, stem):
    ff_mpeg = (
        fmpg0
        + fmpg1
        + srcvid
        + fmpg2
        + Acdc(srcvid)
        + " "
        + parent
        + "/"
        + stem
        + ".HEVC"
        + ".mp4"
    )
    # print()
    # print(ff_mpeg)
    # print()
    ffmpeg = shlex.split(ff_mpeg)
    p9 = subprocess.Popen(ffmpeg, preexec_fn=os.setsid)
    p9.communicate()
    return


clean264 = dict()


# if __name__ == "__main__":
manager = multiprocessing.Manager()
jobs = []
for path1 in Path(ip).rglob("*"):
    # print(probe_file(path1))
    if probe_file_codec(path1) != "h264":
        continue
    # path2 = str(path1)
    # print(path1)
    return2 = manager.list()
    convert = multiprocessing.Process(
        target=convert2hevc,
        args=(str(path1), str(path1.parent), str(path1.stem)),
    )
    jobs.append(convert)
    logging.info("starting transcode of: {}".format(str(path1)))
    convert.start()
    clean264[str(path1)] = str(path1.parent) + "/" + str(path1.stem) + ".HEVC.mp4"
    # print("jobs: ", jobs)
    while True:
        procName = "ffmpeg"
        time.sleep(2)
        if int(getTemp()) > 90:
            procPid = ""
            for proc in psutil.process_iter():
                if proc.name() == procName:
                    procPid = proc.pid
            logging.info("pausing ffmpeg")
            os.kill(procPid, signal.SIGSTOP)
            print("paused!")
            time.sleep(30)
            print("resuming")
            logging.info("resuming ffmpeg")
            os.kill(procPid, signal.SIGCONT)
        if not convert.is_alive():
            break
for j1 in jobs:
    j1.join()

# clean up another attempt
for k, v in clean264.items():
    # print("k: ", k)
    # print("v: ", v)
    # print("k dur: ", probe_duration(k))
    # print("v dur: ", probe_duration(v))
    if probe_duration(k) == probe_duration(v):
        sz = os.path.getsize(k) - 750000
        if os.path.getsize(v) < sz:
            logging.info(" trashing {}".format(k))
            print("trash", k)
            send2trash.send2trash(k)
        else:
            logging.info("check file size on {}".format(k))
            print("log, see if worth converting")
        # print(os.path.getsize(k))
        # print(os.path.getsize(v))

        # send2trash.send2trash(k)
        # logging.info("trashing {}".format(k))

# clean up
# for files in Path(ip).rglob("*"):
#     if is265(str(files)) is True:
#         list265[files.stem] = files
#     elif is264(str(files)) is True:
#         list264[files.stem] = files
#     else:
#         continue
# for k in list265.keys():
#     print(list265[k])
#     if k in list264.keys():
#         print(list264[k])
#         # logging.info
