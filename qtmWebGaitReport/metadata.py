# -*- coding: utf-8 -*-

import os
import xml.etree.cElementTree as ET
from glob import glob
from os import path

from qtmWebGaitReport import c3dValidation, qtools


def get_creation_date(file):
    stat = os.stat(file)
    try:
        return stat.st_birthtime
    except AttributeError:
        return stat.st_mtime


class Metadata:
    def __init__(self, workingDirectory, modelledC3dfilenames, subjectMetadata, creationDate):
        self.workingDirectory = workingDirectory
        self.subjectMetadata = subjectMetadata
        self.modelledC3dfilenames = modelledC3dfilenames
        self.creationDate = creationDate

        c3dValObj = c3dValidation.c3dValidation(self.workingDirectory)
        # self.fileNames = c3dValObj.getValidC3dList(False)
        self.fileNames = []
        for filename in self.modelledC3dfilenames:
            self.fileNames.append(str(path.join(self.workingDirectory, filename)))

    def medatadaInfo(self):
        for filename in self.fileNames:

            measurementName = path.basename(filename)
            measurementName = measurementName.replace(".c3d", "")
            info = []

            # self.getMetaValue(measurementName,"MANUFACTURER","COMPANY")
            generatedByType = "UNSPECIFIED"
            # self.getMetaValue(measurementName,"MANUFACTURER","SOFTWARE")
            name = "UNSPECIFIED"
            # self.getMetaValue(measurementName,"MANUFACTURER","VERSION_LABEL")
            version = "UNSPECIFIED"

            generatedBy = [{"type": "".join(generatedByType), "name": "".join(name), "version": "".join(version)}]

            fields = [
                {"id": "Creation date", "value": str(self.creationDate.date()), "type": "text"},
                {"id": "Creation time", "value": str(self.creationDate.time()), "type": "text"},
            ]

            # add fields from subject metadata
            for key, val in self.subjectMetadata.items():
                fields.append({"id": key, "value": val, "type": "text"})

            info = {"isUsingStandardUnits": True, "generatedBy": generatedBy, "customFields": fields}

        return info

    def subjectInfo(self):
        subject = {
            "id": self.subjectMetadata["Patient ID"] + "_" + self.subjectMetadata["Date of birth"],
            "displayName": self.subjectMetadata["Display name"],
        }
        return subject

    def projectInfo(self):
        project = {"type": "Gait", "subtype": self.subjectMetadata["Sub Session Type"]}
        return project

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
        file = open(filename, "r")
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

    def getMetaValue(self, measurementName, groupLabelName, scalarName):
        acq = qtools.fileOpen(self.workingDirectory + measurementName + ".c3d")
        md = acq.GetMetaData()
        fieldFormat = md.FindChild(groupLabelName).value().FindChild(scalarName).value().GetInfo().GetFormatAsString()
        scalarValue = list()

        if fieldFormat == "Char":
            sValue = md.FindChild(groupLabelName).value().FindChild(scalarName).value().GetInfo().ToString()
            sValue = list(sValue)
            scalarValue = [i.rstrip() for i in sValue]
        else:
            scalarValue = md.FindChild(groupLabelName).value().FindChild(scalarName).value().GetInfo().ToDouble()
        return scalarValue
