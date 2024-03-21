# -*- coding: utf-8 -*-

from os import path

import numpy as np
from pyCGM2.Lib import analysis

from pyCGM2.Processing.Scores import scoreFilters, scoreProcedures
from pyCGM2.Report import normativeDatasets

from qtmWebGaitReport import c3dValidation, signalMapping


class MAP:
    def __init__(self, workingDirectory):
        self.workingDirectory = workingDirectory
        self.null = None

        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.measurementNames = c3dValObj.getValidC3dList(True)
        self.fileNames = c3dValObj.getValidC3dList(False)
        self.normative_dataset = normativeDatasets.NormativeData("Schwartz2008", "Free")
        analysis_per_file = {
            path.basename(name).replace(".c3d", ""): analysis.makeAnalysis(
                workingDirectory + "\\", [path.basename(name)]
            )
            for name in self.fileNames
        }
        self.scores = {}
        for filename, analysis_obj in analysis_per_file.items():
            gps = scoreProcedures.CGM1_GPS(pointSuffix=None)
            scf = scoreFilters.ScoreFilter(gps, analysis_obj, self.normative_dataset)
            scf.compute()
            self.scores[filename] = analysis_obj

    def getAllGVS(self):

        mapSignalNames = [
            "Left Pelvic Angles",
            "Left Hip Angles",
            "Left Knee Angles",
            "Left Ankle Angles",
            "Left Foot Progression",
            "Right Pelvic Angles",
            "Right Hip Angles",
            "Right Knee Angles",
            "Right Ankle Angles",
            "Right Foot Progression",
        ]
        component_idx_name = [(0, "X"), (1, "Y"), (2, "Z")]
        gvs_pycgm2 = {}
        for measurementName in self.measurementNames:
            scores = self.scores[measurementName]
            for sigName in mapSignalNames:
                for idx, component in component_idx_name:
                    gvs_pycgm2[sigName + "_" + component + "_gvs_ln_mean"] = {}

                    for origSigName, ourSigName in signalMapping.sigNameMap.items():
                        if ourSigName == sigName:
                            pigSigName = origSigName
                            side = "Left" if "Left" in ourSigName else "Right"
                    if (pigSigName, side) in scores.gvs.keys():
                        cur_score_values = scores.gvs[(pigSigName, side)]["mean"]
                        gvs_pycgm2[sigName + "_" + component + "_gvs_ln_mean"][measurementName] = np.log(
                            cur_score_values[idx]
                        )

        return gvs_pycgm2

    def getAllGPS(self):
        GPSLeft_pycgm2 = {}
        GPSRight_pycgm2 = {}
        GPSOverall_pycgm2 = {}

        for measurementName in self.measurementNames:
            GPSLeft_pycgm2[measurementName] = np.log(self.scores[measurementName].gps["Context"]["Left"]["mean"][0])
            GPSRight_pycgm2[measurementName] = np.log(self.scores[measurementName].gps["Context"]["Right"]["mean"][0])
            GPSOverall_pycgm2[measurementName] = np.log(self.scores[measurementName].gps["Overall"]["mean"][0])

        return (GPSLeft_pycgm2, GPSRight_pycgm2, GPSOverall_pycgm2)

    def getNormValuesFromV3DXml(self, xmlObj, sigName):
        normValues = str()
        for child in xmlObj[0][0][0]:
            if sigName in child.attrib["value"]:
                normValues = child[1].attrib["data"]
                normValues = np.fromstring(normValues, dtype=float, count=-1, sep=",")
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

        for k, v in gpsScoreData.items():
            if np.all(np.isnan(v) == False):
                gpsData.append({"measurement": k, "values": [v], "rate": self.null})

        gpsOut.append({"id": signame, "type": "scalar", "set": side, "data": gpsData})
        return gpsOut
