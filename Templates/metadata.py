# -*- coding: utf-8 -*-

import qtools
from os import path
from glob import glob
import xml.etree.cElementTree as ET
from datetime import datetime
import c3dValidation

#workingDirectory = "E:\\Qualisys_repository\\Gait-Web-Importer\\Data\\myMess\\"

class Metadata:
    def __init__(self,workingDirectory):
        self.workingDirectory = workingDirectory
        
        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def medatadaInfo(self):
        for filename in self.fileNames:
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            info = []

            type = self.getMetaValue(measurementName,"MANUFACTURER","COMPANY")
            name =  self.getMetaValue(measurementName,"MANUFACTURER","SOFTWARE")
            version =  self.getMetaValue(measurementName,"MANUFACTURER","VERSION_LABEL")
            
            creationDateTimeStr = self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["CREATIONDATEANDTIME"]
            creationDate = str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S").date())
            creationTime = str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S").time())

            diagnosis = self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["DIAGNOSIS"]
            patientName = self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["NAME"]
            bodyHeight = float(self.getSettingsFromTextfile(glob(self.workingDirectory + "*.mp")[0])["$Height"]) / 1000
            bodyWeight = float(self.getSettingsFromTextfile(glob(self.workingDirectory + "*.mp")[0])["$Bodymass"])
            
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
            
            info = {"isUsingStandardUnits": True,
                     "generatedBy": generatedBy,
                     "customFields": fields}

        return info
    
    def subjectInfo(self):
        creationDateTimeStr = self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["CREATIONDATEANDTIME"]
        id = str(datetime.strptime(creationDateTimeStr,"%Y,%m,%d,%H,%M,%S"))
        
        patientName = self.getSettingsFromTextfile(glob(self.workingDirectory + "*Session.enf")[0])["NAME"]
        subject = {
        		"id": id,
        		"displayName": patientName
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
        with open(filename) as file:
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

if __name__ == "__main__":
    a = Metadata(workingDirectory)
    b = a.medatadaInfo()
    #print b