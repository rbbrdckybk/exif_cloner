# Copyright 2025, Bill Kennedy
# SPDX-License-Identifier: MIT

##########################################################################################
# EXIF cloning utility
# Attempts to bulk copy EXIF metadata from files in a source directory tree to similarly-
# named files in a target directory. Will copy original file creation date and GPS coords.
##########################################################################################

# usage/help:
# python exif-cloner.py -h

# example:
# python exif-cloner.py --exiftool_path="C:\utils\exiftool-13.19_64" --source_path="C:\raw_videos" --target_path="C:\processed_videos" --ext "mov, mp4"

import sys
import os
import re
import glob
import argparse
import subprocess
from os.path import exists
from pathlib import Path

# gets resources found within specified dir
def get_resources_from_dir(root_dir, valid_ext):
    resources = []
    for name in os.listdir(root_dir):
        full_file_path = os.path.join(root_dir, name)
        if os.path.isfile(full_file_path):
            if (name.lower().endswith(valid_ext)):
                resources.append(full_file_path)
    resources = list(set(resources))
    resources.sort()
    return resources

# gets resources found within specified dir and all sub-dirs
def get_resources_from_tree(root_dir, valid_ext):
    resources = []
    for root, dirs, files in os.walk(root_dir, topdown=False):
        for name in files:
            if (name.lower().endswith(valid_ext)):
                full_file_path = os.path.join(root, name)
                resources.append(full_file_path)
        for name in dirs:
            full_dir_path = os.path.join(root, name)
    resources = list(set(resources))
    resources.sort()
    return resources

# find corresponding source file, given target filename without extension
def find_matching_source(target_filename, source_list):
    match = ''
    if target_filename != '':
        for f in source_list:
            # strip path/ext from original filename to compare to target
            orig_fn = os.path.basename(f).rsplit('.', 1)[0]
            if orig_fn in target_filename:
                match = f
                break
    return match

# entry point
if __name__ == '__main__':
    print('\nStarting..')

    # define command-line args
    ap = argparse.ArgumentParser()
    ap.add_argument(
        '--exiftool_path',
        type=str,
        required=True,
        default='',
        help='path to exiftool.exe'
    )
    ap.add_argument(
        '--source_path',
        type=str,
        required=True,
        default='',
        help='path of original files containing EXIF metadata to clone'
    )
    ap.add_argument(
        '--target_path',
        type=str,
        required=True,
        default='',
        help='path of target files to process'
    )
    ap.add_argument(
        '--model',
        type=str,
        default='',
        help='device/camera model info to add to EXIF data'
    )
    ap.add_argument(
        '--ext',
        type=str,
        default='mov, mp4, mkv',
        help='comma delimited list of file extensions to inspect for source metadata'
    )
    options = ap.parse_args()

    # build list of valid relevant file extensions for metadata inspection
    valid = []
    extensions = str(options.ext).split(',')
    for ext in extensions:
        ext = '.' + ext.replace('.', '').strip()
        valid.append(ext)
    valid = tuple(valid)

    # check that user-specified paths exist; build list of source and target files
    exiftool_full_path = os.path.join(options.exiftool_path, 'exiftool.exe')
    if os.path.exists(exiftool_full_path):
        print('Using ' + exiftool_full_path + '...')
    else:
        print('Error: exiftool.exe not found at "' + exiftool_full_path + '"; aborting...')
        exit(-1)

    source_files = []
    if os.path.exists(options.source_path):
        print('Building list of source files in "' + options.source_path + '"...')
        source_files = get_resources_from_tree(options.source_path, valid)
    else:
        print('Error: "' + options.source_path + '" does not exist; aborting...')
        exit(-1)
    if len(source_files) == 0:
        print('Error: "' + options.source_path + '" contains no files with valid extensions; aborting...')
        exit(-1)

    if os.path.exists(options.target_path):
        print('Processing files in "' + options.target_path + '"...')
    else:
        print('Error: "' + options.target_path + '" does not exist; aborting...')
        exit(-1)

    files = get_resources_from_dir(options.target_path, valid)
    print('Found ' + str(len(files)) + ' target files in "' + options.target_path + '":')

    # process files
    success = 0
    count = 0
    for f in files:
        count += 1
        print('\n [' + str(count) + '] Working on ' + f + '...')
        # strip off path and extension from filename
        t_filename = os.path.basename(f).rsplit('.', 1)[0]
        match = find_matching_source(t_filename, source_files)
        if match != '':
            print('    Original file appears to be: ' + match)
            # get original exif metadata from source file
            command = '"' + exiftool_full_path + '"' + ' -ee -n ' + '"' + match + '"'
            print('    Reading source file...')
            p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            dtime = ''
            gps = ''
            for line in p.stdout.readlines():
                l = line.decode('utf-8')
                if 'File Creation Date/Time' in l:
                    dtime = l.split(':', 1)[1].strip()
                elif 'GPS Position' in str(line):
                    gps = l.split(':', 1)[1].strip()
            retval = p.wait()

            command = '"' + exiftool_full_path + '" -overwrite_original'
            write = False
            if options.model != '':
                command += ' -model="' + options.model + '"'
                write = True
            if dtime != '':
                print('     - Extracted creation date/time: ' + dtime)
                command +=  ' -CreateDate="' + dtime + '"'
                write = True
            if gps != '':
                print('     - Extracted GPS coords: ' + gps)
                command +=  ' -gpsposition="' + gps + '"'
                write = True

            # write exif to target file
            if write:
                command += ' "' + f + '"'
                print('    Attempting to update...')
                p = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                for line in p.stdout.readlines():
                    l = line.decode('utf-8')
                    if '1 image files updated' in l:
                        success += 1
                        print('    Successfully updated EXIF metadata.')
                    else:
                        print('  * Unexpected result:')
                        print(' -> ' + l)
                retval = p.wait()
            else:
                print('    Failed to find any relevant EXIF metadata in original; skipping...')
        else:
            print('    Original source file could not be located; skipping...')

    print('\n' + str(success) + ' file(s) updated.')
    print('Done!\n')
