# EXIF_Cloner Utility

Quick command-line utility for bulk cloning EXIF metadata from a source directory (or tree) full of media files to a target directory (also full of media files). EXIF_Cloner uses [ExifTool](https://exiftool.org/) in the background, which you'll need to download and point it at.

![EXIF_Cloner screenshot](https://github.com/rbbrdckybk/exif_cloner/blob/main/screenshot.jpg?raw=true)

For example, if you have a bunch of original raw video files that contain embedded EXIF data (original creation date/time, GPS coordinates, etc) like so:
```
C:\raw_video\20250222\DJI_0213.mp4
C:\raw_video\20250223\beach\DJI_0215.mov
C:\raw_video\20250225\DJI_0218.mp4
...
```
And you have another folder full of processed videos that are named similarly to the originals (in this case, the processed files all start with the original filename).
```
C:\processed_video\DJI_0213_0008_D00000178.mp4
C:\processed_video\DJI_0215_0003_D00000276.mp4
C:\processed_video\DJI_0218_0006_D00000977.mp4
...
```
Then you can use EXIF_Cloner to bulk copy the EXIF date/time & GPS info from the source files to the processed files like so:
```
python exif-cloner.py --source_path="C:\raw_video" --target_path="C:\processed_video" --ext "mp4, mov" --exiftool_path="C:\apps\exiftool" 
```
I wrote this in about an hour after getting frustrated that I kept losing my metadata when editing videos with Davinci and other tools, causing my edited media to show up with the incorrect date and no GPS data in my Immich library. I've run hundreds of videos through it it without issues, but no guarantees that it'll work flawlessly for your use case. I've only tested on Windows but it should work fine in Linux as well.

# Usage

Clone this repo or simply download **exif-cloner.py** and run ```python exif-cloner.py -h``` for help.
