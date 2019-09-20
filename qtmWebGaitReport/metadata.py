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
    def __init__(self,workingDirectory, modelledC3dfilenames,subjectMd,creationDate ):
        self.workingDirectory = workingDirectory
        self.subjectMd  = subjectMd
        self.modelledC3dfilenames = modelledC3dfilenames
        self.creationDate = creationDate

        c3dValObj = c3dValidation.c3dValidation(self.workingDirectory)
        #self.fileNames = c3dValObj.getValidC3dList(False)
        self.fileNames = []
        for filename in self.modelledC3dfilenames:
            self.fileNames.append(str(self.workingDirectory+filename))



    def medatadaInfo(self):
        for filename in self.fileNames:


            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            info = []

            type = "UNSPECIFIED"#self.getMetaValue(measurementName,"MANUFACTURER","COMPANY")
            name =  "UNSPECIFIED"#self.getMetaValue(measurementName,"MANUFACTURER","SOFTWARE")
            version =  "UNSPECIFIED"#self.getMetaValue(measurementName,"MANUFACTURER","VERSION_LABEL")

            creation_date = datetime.fromtimestamp(get_creation_date(filename))
            creationDate = str(creation_date.date())#str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S").date())
            creationTime = str(creation_date.time())#str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S").time())

            diagnosis = "UNSPECIFIED"#self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["DIAGNOSIS"]
            patientName = "UNSPECIFIED"#self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["NAME"]

            generatedBy = [{
            			"type": ''.join(type),
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
                        "value": self.subjectMd["diagnosis"],
                        "type": "text"},
                        {
                        "id": "Last name",
                        "value": self.subjectMd["patientName"],
                        "type": "text"},
                        {
                        "id": "Height",
                        "value": self.subjectMd["bodyHeight"],
                        "type": "text"},
                        {
                        "id": "Weight",
                        "value": self.subjectMd["bodyWeight"],
                        "type": "text"},
                        {
                        "id": "Dob",
                        "value": self.subjectMd["dob"],
                        "type": "text"},
                        {
                        "id": "Sex",
                        "value": self.subjectMd["sex"],
                        "type": "text"},
                        {
                        "id": "Test condition",
                        "value": self.subjectMd["test condition"],
                        "type": "text"},
                    ]

            info = {"isUsingStandardUnits": True,
                     "generatedBy": generatedBy,
                     "customFields": fields}

        return info

    def subjectInfo(self):
        #creationDateTimeStr = "2019,6,12,12,54,7"#self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["CREATIONDATEANDTIME"]
        id = str(self.creationDate)#str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S"))

        patientName = self.subjectMd["patientName"]#self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["NAME"]
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

    def getMetaValue(self,measurementName,groupLabelName,scalarName):
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

#a = Metadata(workingDirectory)
#b = a.subjectInfo()
#print b
