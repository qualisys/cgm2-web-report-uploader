# -*- coding: utf-8 -*-

import os
from glob import glob
from ffmpy import FFmpeg


def get_mp4_filepaths(working_directory):
    mp4_file_paths = list(glob(os.path.join(working_directory, "*.mp4")))
    return mp4_file_paths


def get_mp4_filenames(working_directory):
    mp4_file_paths = get_mp4_filepaths(working_directory)
    output_filenames = [os.path.basename(x) for x in mp4_file_paths]
    return output_filenames


def get_parent_folder_absolute_path(folder):
    return os.path.abspath(os.path.join(folder, os.pardir))


class AviToMp4:
    templatesDirectory = os.path.dirname(__file__)
    ffmpeg = os.path.join(templatesDirectory, "ffmpeg/bin/ffmpeg.exe")

    def __init__(self, workingDirectory):
        self.workingDirectory = workingDirectory
        self.aviFilePath = glob(os.path.join(self.workingDirectory, "*.avi"))

    def convertAviToMp4(self):
        for inputFilename in self.aviFilePath:
            outputFileName = inputFilename.replace("avi", "mp4")
            ff = FFmpeg(
                executable=self.ffmpeg,
                inputs={inputFilename: None},
                outputs={
                    outputFileName: "-y -pix_fmt yuv420p -vcodec libx264 -profile:v baseline -level 3.0 -g 15 -s 720x404 -b:v 1000k -an -bufsize 2000k"
                },
            )
            ff.run()

    def getMp4Filenames(self, basenameOnly):
        outputFileNames = []
        for inputFilename in self.aviFilePath:
            if basenameOnly == True:
                inputFilename = os.path.basename(inputFilename)
            outputFileName = inputFilename.replace("avi", "mp4")
            outputFileNames.append(outputFileName)
        return outputFileNames
