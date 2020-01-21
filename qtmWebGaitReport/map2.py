# -*- coding: utf-8 -*-
import qtmWebGaitReport
import qtools
from os import path, getcwd
import numpy as np
import signalMapping
import scipy.signal
import xml.etree.cElementTree as ET
import c3dValidation


class MAP:
    def __init__(self, workingDirectory):
        self.workingDirectory = workingDirectory
        self.null = None

        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.measurementNames = c3dValObj.getValidC3dList(True)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def calculateGVS(self):

        mapSignalNames = ["Left Pelvic Angles", "Left Hip Angles", "Left Knee Angles", "Left Ankle Angles", "Left Foot Progression",
                          "Right Pelvic Angles", "Right Hip Angles", "Right Knee Angles", "Right Ankle Angles", "Right Foot Progression"]
        components = {'X', 'Y', 'Z'}
        measuredValuesNormalized = {}
        gvs = {}
        gvsLn = {}

        tree = ET.parse(path.join(qtmWebGaitReport.GAIT_WEB_REPORT_PATH, "qtmWebGaitReport", "Normatives",
                                  "normatives.xml"))
        xmlRoot = tree.getroot()

        for sigName in mapSignalNames:
            measuredValuesNormalized[sigName] = {}

            for component in components:
                gvs[sigName + "_" + component + "_gvs"] = {}
                gvsLn[sigName + "_" + component + "_gvs_ln_mean"] = {}

                normValues = self.getNormValuesFromV3DXml(
                    xmlRoot, sigName + "_" + component)

                if normValues is not "":
                    if component == "X":
                        i = 0
                    elif component == "Y":
                        i = 1
                    elif component == "Z":
                        i = 2

                    for filename in self.fileNames:
                        acq = qtools.fileOpen(filename)
                        measurementName = path.basename(filename)
                        measurementName = measurementName.replace('.c3d', '')

                        measuredValuesNormalized[sigName][measurementName] = {}
                        gvs[sigName + "_" + component +
                            "_gvs"][measurementName] = {}
                        gvsLn[sigName + "_" + component +
                              "_gvs_ln_mean"][measurementName] = {}

                        for origSigName, ourSigName in signalMapping.sigNameMap.iteritems():
                            if ourSigName == sigName:
                                pigSigName = origSigName

                        signal = acq.GetPoint(pigSigName)
                        measuredValues = scipy.signal.resample(
                            signal.GetValues(), 101)  # normalize to 101 points
                        measuredValuesNormalized[sigName][measurementName] = measuredValues

                        sub = measuredValuesNormalized[sigName][measurementName][:,
                                                                                 i] - normValues
                        gvs[sigName + "_" + component +
                            "_gvs"][measurementName] = qtools.rootMeanSquared(sub)
                        gvsLn[sigName + "_" + component + "_gvs_ln_mean"][measurementName] = np.log(
                            gvs[sigName + "_" + component + "_gvs"][measurementName])

        return(gvs, gvsLn)

    def calculateGPS(self):
        GPSLeft = {}
        GPSRight = {}
        GPSOverall = {}

        for measurementName in self.measurementNames:
            gvs = self.calculateGVS()[0]

            GPSLeft[measurementName] = np.sqrt(
                self.getGVS(gvs, measurementName, "Left Ankle Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Left Foot Progression_Z")**2 +
                self.getGVS(gvs, measurementName, "Left Hip Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Left Hip Angles_Y")**2 +
                self.getGVS(gvs, measurementName, "Left Hip Angles_Z")**2 +
                self.getGVS(gvs, measurementName, "Left Knee Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Left Pelvic Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Left Pelvic Angles_Y")**2 +
                self.getGVS(gvs, measurementName, "Left Pelvic Angles_Z")**2
            ) / 9
            GPSRight[measurementName] = np.sqrt(
                self.getGVS(gvs, measurementName, "Right Ankle Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Right Foot Progression_Z")**2 +
                self.getGVS(gvs, measurementName, "Right Hip Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Right Hip Angles_Y")**2 +
                self.getGVS(gvs, measurementName, "Right Hip Angles_Z")**2 +
                self.getGVS(gvs, measurementName, "Right Knee Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Right Pelvic Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Right Pelvic Angles_Y")**2 +
                self.getGVS(gvs, measurementName, "Right Pelvic Angles_Z")**2
            ) / 9
            GPSOverall[measurementName] = np.sqrt(
                self.getGVS(gvs, measurementName, "Left Ankle Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Left Foot Progression_Z")**2 +
                self.getGVS(gvs, measurementName, "Left Hip Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Left Hip Angles_Y")**2 +
                self.getGVS(gvs, measurementName, "Left Hip Angles_Z")**2 +
                self.getGVS(gvs, measurementName, "Left Knee Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Left Pelvic Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Left Pelvic Angles_Y")**2 +
                self.getGVS(gvs, measurementName, "Left Pelvic Angles_Z")**2 +
                self.getGVS(gvs, measurementName, "Right Ankle Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Right Foot Progression_Z")**2 +
                self.getGVS(gvs, measurementName, "Right Hip Angles_X")**2 +
                self.getGVS(gvs, measurementName, "Right Hip Angles_Y")**2 +
                self.getGVS(gvs, measurementName, "Right Hip Angles_Z")**2 +
                self.getGVS(gvs, measurementName, "Right Knee Angles_X")**2
            ) / 15
        return(GPSLeft, GPSRight, GPSOverall)

    def getNormValuesFromV3DXml(self, xmlObj, sigName):
        normValues = str()
        for child in xmlObj[0][0][0]:
            if sigName in child.attrib["value"]:
                normValues = child[1].attrib["data"]
                normValues = np.fromstring(
                    normValues, dtype=float, count=-1, sep=",")
        return normValues

    def getGVS(self, gvs, measurementName, signame):
        out = 0.0
        for k, v in gvs.items():
            if signame in k:
                for k1, v1 in v.items():
                    if measurementName in k1:
                        out = v1
        return out

    def gpsExport(self, gpsScoreData, signame, frameRate):
        gpsData = list()
        gpsOut = list()

        if "Left" in signame:
            side = "left"
        elif "Right" in signame:
            side = "right"
        else:
            side = self.null

        for k, v in gpsScoreData.iteritems():
            gpsData.append({
                "measurement": k,
                "values": [v],
                "rate": self.null
            })

        gpsOut.append({"id": signame,
                       "type": "scalar",
                       "set": side,
                       "data": gpsData
                       })
        return gpsOut
