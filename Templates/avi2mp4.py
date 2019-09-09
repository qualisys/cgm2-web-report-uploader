# -*- coding: utf-8 -*-

from os import path
from glob import glob
from ffmpy import FFmpeg
#import subprocess

workingDirectory = "E:\\Qualisys_repository\\Gait-Web-Importer\\Data\\Oxford\\"

class AviToMp4:
    templatesDirectory = path.dirname(__file__)
    ffmpeg = path.join(templatesDirectory, 'ffmpeg/bin/ffmpeg.exe')

    def __init__(self,workingDirectory):
        self.workingDirectory = workingDirectory
        self.aviFilePath = glob(self.workingDirectory + "*.avi")

    def convertAviToMp4(self):
        for inputFilename in self.aviFilePath:
            outputFileName = inputFilename.replace('avi','mp4')
            ff = FFmpeg(executable=self.ffmpeg,
                   inputs={inputFilename: None},
                   outputs={outputFileName: '-y -pix_fmt yuv420p -vcodec libx264 -profile:v baseline -level 3.0 -g 15 -s 720x404 -b:v 1000k -an -bufsize 2000k'} 
                   )
            ff.run()
            
#    def convert_avi_to_mp4(self):
#        for inputFilename in self.aviFilePath:
#            outputFileName = inputFilename.replace('avi','mp4')
#            subprocess.Popen("ffmpeg -i '{input}' -y -pix_fmt yuv420p -vcodec libx264 -profile:v baseline -level 3.0 -g 15 -s 720x404 -b:v 1000k -an -bufsize 2000k '{output}'".format(input = inputFilename, output = outputFileName),shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#        return True

    def getMp4Filenames(self,basenameOnly):
        outputFileNames = []
        for inputFilename in self.aviFilePath:
            if basenameOnly == True:
                inputFilename = path.basename(inputFilename)
            outputFileName = inputFilename.replace('avi','mp4')
            outputFileNames.append(outputFileName)
        return outputFileNames
        
if __name__ == "__main__":
    a = AviToMp4(workingDirectory)
    b = a.convertAviToMp4()

