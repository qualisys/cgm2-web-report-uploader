# -*- coding: utf-8 -*-

from os import path
from glob import glob
from ffmpy import FFmpeg


class AviToMp4:
    templatesDirectory = path.dirname(__file__)
    ffmpeg = path.join(templatesDirectory, 'ffmpeg/bin/ffmpeg.exe')

    def __init__(self, workingDirectory):
        self.workingDirectory = workingDirectory
        self.aviFilePath = glob(path.join(self.workingDirectory, "*.avi"))

    def convertAviToMp4(self):
        for inputFilename in self.aviFilePath:
            outputFileName = inputFilename.replace('avi', 'mp4')
            ff = FFmpeg(executable=self.ffmpeg,
                        inputs={inputFilename: None},
                        outputs={
                            outputFileName: '-y -pix_fmt yuv420p -vcodec libx264 -profile:v baseline -level 3.0 -g 15 -s 720x404 -b:v 1000k -an -bufsize 2000k'}
                        )
            ff.run()

    def getMp4Filenames(self, basenameOnly):
        outputFileNames = []
        for inputFilename in self.aviFilePath:
            if basenameOnly == True:
                inputFilename = path.basename(inputFilename)
            outputFileName = inputFilename.replace('avi', 'mp4')
            outputFileNames.append(outputFileName)
        return outputFileNames
