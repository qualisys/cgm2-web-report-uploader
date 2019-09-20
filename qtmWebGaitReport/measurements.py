# -*- coding: utf-8 -*-

import qtools
import os
from os import path
from glob import glob
import xml.etree.cElementTree as ET
from datetime import datetime
import avi2mp4
import c3dValidation

from datetime import datetime

#workingDirectory = "E:\\OneDrive\\qualisys.se\\App Team - Documents\\Projects\\Gait web reports from Vicon c3d data\\Python parser\\Data\\Oxford\\"

def get_creation_date(file):
    stat = os.stat(file)
    try:
        return stat.st_birthtime
    except AttributeError:
        return stat.st_mtime



class Measurements:
    def __init__(self,workingDirectory):
        self.workingDirectory = workingDirectory

        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def measurementInfo(self):
        info = []

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            resources = []

            val = acq.GetDuration()
            startOffset = acq.GetFirstFrame() / acq.GetPointFrequency()
            frameRate = acq.GetPointFrequency()#self.getValueFromXMLSystem("Capture","MeasuredFrameRate")
            originalDuration = acq.GetDuration()#self.getValueFromXMLSystem("Capture","FramesCaptured") / frameRate
            creationDateTimeStr = "2019,6,12,12,54,7"#self.getSettingsFromTextfile(glob(self.workingDirectory + "*" + measurementName + ".Trial" +"*"+ ".enf")[0])["CREATIONDATEANDTIME"]
            creation_date = datetime.fromtimestamp(get_creation_date(filename))
            creationDate = str(creation_date.date())#str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S").date())
            creationTime = str(creation_date.time())#str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S").time())

            # if "DIAGNOSIS" in self.getSettingsFromTextfile(glob(self.workingDirectory + "*" + measurementName + ".Trial" +"*"+ ".enf")[0]):
            #     diagnosis = self.getSettingsFromTextfile(glob(self.workingDirectory + "*" + measurementName + ".Trial" +"*"+ ".enf")[0])["DIAGNOSIS"]
            # else:
            #     diagnosis = ""
            diagnosis =""

            patientName = "UNSPECIFIED"#self.getSettingsFromTextfile(glob(self.workingDirectory + "*" + measurementName + ".Trial" +"*"+ ".enf")[0])["NAME"]
            bodyHeight = 0#float(self.getSettingsFromTextfile(glob(self.workingDirectory + "*.mp")[0])["$Height"]) / 1000
            bodyWeight = 0#float(self.getSettingsFromTextfile(glob(self.workingDirectory + "*.mp")[0])["$Bodymass"])

            videoObj = avi2mp4.AviToMp4(self.workingDirectory)
            videoFilenames = videoObj.getMp4Filenames(True)

            for videoFilename in videoFilenames:
                videoName = videoFilename.replace('.mp4', '')
                resources.append({
                    			"type": "video",
                    			"name": videoName,
                    			"src": videoFilename})

            fields = [{      "id": "Creation date",
                             "value": creationDate,
                             "type": "text"},
                            {
                             "id": "Creation time",
                             "value": creationTime,
                             "type": "text"},
                            {
                             "id": "Diagnosis",
                             "value": diagnosis,
                             "type": "text"},
                            {
                             "id": "Last name",
                             "value": patientName,
                             "type": "text"},
                            {
                             "id": "Height",
                             "value": bodyHeight,
                             "type": "text"},
                            {
                             "id": "Weight",
                             "value": bodyWeight,
                             "type": "text"},
                            ]

            info.append({"duration": val,
                         "startOffset": startOffset,
                         "originalDuration": originalDuration,
                         "rate": frameRate,
                         "id": measurementName,
                         "fields": fields,
                         "resources": resources
                         })
        return info

    def getValueFromXMLSystem(self, defList, param):
        filename = glob(self.workingDirectory + "*.system")[0]
        tree = ET.parse(filename)
        xmlRoot = tree.getroot()

        for child in xmlRoot:
            if defList in child.attrib["name"]:
                for kid in child[0][0]:
                    if param in kid.attrib["name"]:
                        val = float(kid.attrib["value"])
        return val

    def getSettingsFromTextfile(self,filename):
        file = open(filename, 'r')
        content = file.read()
        lines = content.split("\n")
        settings = {}

        for line in lines:
          parts = line.split("=")
          if len(parts) == 2:
            key = str.strip(parts[0])
            value = str.strip(parts[1])
            settings[key] = value
        return settings

#a = Measurements(workingDirectory)
#creationDate = a.getSettingsFromTextfile(glob(workingDirectory + "*Session.enf")[0])["CREATIONDATEANDTIME"]
##dd = datetime.strptime(str(creationDate),"%Y-%m-%d %H:%M:%S")
##ddd = datetime.strftime(dd, '%y,%m,%d,%H,%M,%S')
#b = a.measurementInfo()
#print b
