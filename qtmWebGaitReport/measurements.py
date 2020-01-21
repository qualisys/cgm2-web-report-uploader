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


def get_creation_date(file):
    stat = os.stat(file)
    try:
        return stat.st_birthtime
    except AttributeError:
        return stat.st_mtime


class Measurements:
    def __init__(self, workingDirectory):
        self.workingDirectory = workingDirectory

        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def measurementInfo(self):
        info = []

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d', '')
            resources = []

            val = acq.GetDuration()
            startOffset = acq.GetFirstFrame() / acq.GetPointFrequency()
            frameRate = acq.GetPointFrequency()
            originalDuration = acq.GetDuration()
            creation_date = datetime.fromtimestamp(get_creation_date(filename))
            creationDate = str(creation_date.date())
            creationTime = str(creation_date.time())

            diagnosis = ""

            patientName = "UNSPECIFIED"
            bodyHeight = 0
            bodyWeight = 0

            videoObj = avi2mp4.AviToMp4(self.workingDirectory)
            videoFilenames = videoObj.getMp4Filenames(True)

            for videoFilename in videoFilenames:
                videoName = videoFilename.replace('.mp4', '')
                resources.append({
                    "type": "video",
                    "name": videoName,
                    "src": videoFilename})

            fields = [{"id": "Creation date",
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

    def getSettingsFromTextfile(self, filename):
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
