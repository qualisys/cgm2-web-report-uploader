# -*- coding: utf-8 -*-
import qtools
from os import path

#workingDirectory = "E:\\Qualisys_repository\\Gait-Web-Importer\\Data\\FAITest3\\"

class c3dValidation:
    def __init__(self,workingDirectory):
        self.workingDirectory = workingDirectory
        self.c3dFileList = qtools.createC3dFileList(workingDirectory)

    def getValidC3dList(self,basenameOnly):
        measurementNames = []
        fileNames = []
        #check that pluginGait model calculations exist
        #check that events exist

        for filename in self.c3dFileList:
            origLabelNames = []
            acq = qtools.fileOpen(filename)
            noMarkers = range(acq.GetPointNumber())

            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')

            for number in noMarkers: #it is assumed that same signals are in all trials
                marker = acq.GetPoint(number)
                origLabelNames.append(marker.GetLabel())
                
            if "LAnkleAngles" in origLabelNames and acq.GetEventNumber() > 0:
                measurementNames.append(measurementName)
                fileNames.append(filename)
                
            if basenameOnly == True:
                out = measurementNames
            else:
                out = fileNames
        return out
            
#a = c3dValidation(workingDirectory)
#b = a.getValidC3dList(True)
#
