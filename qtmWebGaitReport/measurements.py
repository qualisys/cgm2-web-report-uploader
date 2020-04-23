# -*- coding: utf-8 -*-

import qtools
import os
import yaml
from os import path
from glob import glob
import xml.etree.cElementTree as ET
from datetime import datetime
from avi2mp4 import get_mp4_filenames
from avi2mp4 import get_parent_folder_absolute_path
import c3dValidation

from datetime import datetime


def get_creation_date(file):
    stat = os.stat(file)
    try:
        return stat.st_birthtime
    except AttributeError:
        return stat.st_mtime


def create_resources(video_filenames, extra_settings):

    if "Cameras" in extra_settings.keys():
        all_video_serials = list(extra_settings["Cameras"].keys())
    else:
        all_video_serials = []
    resources = []
    for video_filename in video_filenames:
        video_name = video_filename.replace('.mp4', '')
        cur_resource = {
            "type": "video",
            "name": video_name,
            "src": video_filename,
        }
        current_serial = [
            serial for serial in all_video_serials if str(serial) in video_name]
        if current_serial != []:
            current_serial = current_serial[0]
            if "Group" in extra_settings["Cameras"][current_serial].keys():
                cur_resource["group"] = extra_settings["Cameras"][current_serial]["Group"]
        resources.append(cur_resource)
    return resources


class Measurements:
    def __init__(self, workingDirectory):
        self.workingDirectory = workingDirectory

        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def measurementInfo(self, extra_settings={}):
        info = []

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d', '')

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

            video_filenames = get_mp4_filenames(
                get_parent_folder_absolute_path(self.workingDirectory))
            resources = create_resources(video_filenames, extra_settings)

            fields = [
                {
                    "id": "Creation date",
                    "value": creationDate,
                    "type": "text"
                },
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
                    "type": "text"
                },
            ]

            info.append(
                {
                    "duration": val,
                    "startOffset": startOffset,
                    "originalDuration": originalDuration,
                    "rate": frameRate,
                    "id": measurementName,
                    "fields": fields,
                    "resources": resources
                }
            )
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
