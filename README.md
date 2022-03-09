# video-cleanup

first python app and learning github at the same time.

cleans media files (mkv and mp4 currently) of Title and subtitles by exporting tracks and rebuilding a clean file.
clean up name, and move to Shows to sorted Destination.

/path/to/subs/

/path/to/shows/  Sorts like this ->  Show.Name/S0xE0x/Show.Name.S0xE0x.Codec.Resolution.ext

Requirements: 

mkvtoolnix  "sudo apt install mkvtoolnix" or "https://mkvtoolnix.download/downloads.html"

Send2Trash  "pip install send2trash"      or "https://pypi.org/project/Send2Trash/"
