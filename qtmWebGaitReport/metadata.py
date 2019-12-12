# -*- coding: utf-8 -*-

import qtools
import os
from os import path
from glob import glob
import xml.etree.cElementTree as ET
from datetime import datetime
import c3dValidation


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
            self.fileNames.append(
                str(path.join(self.workingDirectory, filename)))

    def medatadaInfo(self):
        for filename in self.fileNames:

            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d', '')
            info = []

            # self.getMetaValue(measurementName,"MANUFACTURER","COMPANY")
            generatedByType = "UNSPECIFIED"
            # self.getMetaValue(measurementName,"MANUFACTURER","SOFTWARE")
            name = "UNSPECIFIED"
            # self.getMetaValue(measurementName,"MANUFACTURER","VERSION_LABEL")
            version = "UNSPECIFIED"

            creation_date = datetime.fromtimestamp(get_creation_date(filename))
            # str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S").date())
            creationDate = str(creation_date.date())
            # str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S").time())
            creationTime = str(creation_date.time())

            # self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["DIAGNOSIS"]
            diagnosis = "UNSPECIFIED"
            # self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["NAME"]
            patientName = "UNSPECIFIED"

            generatedBy = [{
                "type": ''.join(generatedByType),
                "name": ''.join(name),
                "version": ''.join(version)}
            ]

            fields = [{"id": "Creation date",
                       "value": creationDate,
                       "type": "text"},
                      {
                "id": "Creation time",
                "value": creationTime,
                "type": "text"},
                {
                "id": "Diagnosis",
                "value": self.subjectMetadata["diagnosis"],
                "type": "text"},
                {
                "id": "Last name",
                "value": self.subjectMetadata["patientName"],
                "type": "text"},
                {
                "id": "Height",
                "value": self.subjectMetadata["bodyHeight"],
                "type": "text"},
                {
                "id": "Weight",
                "value": self.subjectMetadata["bodyWeight"],
                "type": "text"},
                {
                "id": "Dob",
                "value": self.subjectMetadata["dob"],
                "type": "text"},
                {
                "id": "Sex",
                "value": self.subjectMetadata["sex"],
                "type": "text"},
                {
                "id": "Test condition",
                "value": self.subjectMetadata["test condition"],
                "type": "text"},
            ]

            info = {"isUsingStandardUnits": True,
                    "generatedBy": generatedBy,
                    "customFields": fields}

        return info

    def subjectInfo(self):
        # creationDateTimeStr = "2019,6,12,12,54,7"#self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["CREATIONDATEANDTIME"]
        # str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S"))
        id = str(self.creationDate)

        # self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["NAME"]
        patientName = self.subjectMetadata["patientName"]
        subject = {
            "id": id,
            "displayName": patientName,
        }
        return subject

    def projectInfo(self):
        project = {
            "type": "Gait",
            "subtype": "Plugin Gait"
        }
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

    def getMetaValue(self, measurementName, groupLabelName, scalarName):
        acq = qtools.fileOpen(self.workingDirectory + measurementName + ".c3d")
        md = acq.GetMetaData()
        fieldFormat = md.FindChild(groupLabelName).value().FindChild(
            scalarName).value().GetInfo().GetFormatAsString()
        scalarValue = list()

        if fieldFormat == "Char":
            sValue = md.FindChild(groupLabelName).value().FindChild(
                scalarName).value().GetInfo().ToString()
            sValue = list(sValue)
            scalarValue = [i.rstrip() for i in sValue]
        else:
            scalarValue = md.FindChild(groupLabelName).value().FindChild(
                scalarName).value().GetInfo().ToDouble()
        return scalarValue
