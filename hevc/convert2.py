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
fmpg0 = "/usr/bin/ffmpeg"
fmpg1 = " -hide_banner -hwaccel auto -i "  # insert src + 2
fmpg2 = (
    " -movflags faststart"
    + " -c:v hevc_nvenc -rc 1"
    + " -rc-lookahead 20 -no-scenecut 0 -cq 27 -c:a "
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


def is264(srcvid):
    for stream in FFProbe(srcvid).streams:
        if stream.is_video():
            if stream.codec_name == "h264":
                return True


def is265(srcvid):
    for stream in FFProbe(srcvid).streams:
        if stream.is_video():
            if stream.codec_name == "h265":
                return True


def Acdc(srcvid):
    for stream in FFProbe(srcvid).streams:
        if stream.is_audio():
            return stream.codec_name


def convert2hevc(srcvid, parent, stem):
    if is264(srcvid) is not True:
        print("not h264, quitting")
        quit()
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
    print()
    print(ff_mpeg)
    print()
    ffmpeg = shlex.split(ff_mpeg)
    p9 = subprocess.Popen(ffmpeg, preexec_fn=os.setsid)
    p9.communicate()
    return


def cleanOld():
    for files in Path(ip).rglob("*"):
        if is265(str(files)) is not True:
            continue
        match1 = files.stem
        for file in Path(ip).rglob("*"):
            if is264(str(file)) is not True:
                continue
            if file.stem == match1:
                send2trash.send2trash(file)
                logging.info("trashing: ", file)
            else:
                continue


if __name__ == "__main__":
    manager = multiprocessing.Manager()
    jobs = []
    for path1 in Path(ip).rglob("*"):
        if is264(str(path1)) is not True:
            continue
        return2 = manager.list()
        convert = multiprocessing.Process(
            target=convert2hevc,
            args=(str(path1), str(path1.parent), str(path1.stem)),
        )
        jobs.append(convert)
        logging.info("starting transcode of: ", str(path1))
        convert.start()
        print("jobs: ", jobs)
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
    cleanOld()
