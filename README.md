# video-cleanup

Works in debian/ubuntu/Pop OS and Windows

first python app and learning github at the same time.

cleans media files (mkv and mp4 currently) of Title and subtitles by exporting tracks and rebuilding a clean file, maintains any chapters if they exist.
clean up name, and move to Shows to sorted Destination.

/path/to/subs/

/path/to/shows/  Sorts like this ->  Show.Name/Season.xx/Show.Name.S0xE0x.Codec.Resolution.ext
--> /path/to/shows/Show.Name/ must exist but Season.xx will be auto created if needed.

Requirements: 

mkvtoolnix  "sudo apt install mkvtoolnix" or https://mkvtoolnix.download/downloads.html

ffmpeg    "sudo apt install ffmpeg"       or https://ffmpeg.org/download.html
          
          sudo apt install libmediainfo-dev

Send2Trash  "pip install send2trash"      or https://pypi.org/project/Send2Trash/

pymediainfo "pip install pymediainfo"     or https://pypi.org/project/pymediainfo/

psutil      "pip install psutil"          or https://pypi.org/project/psutil/

