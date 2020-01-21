# -*- coding: utf-8 -*-
import qtools
from os import path
import numpy as np
import signalMapping
from glob import glob
import metadata
import c3dValidation


def _getSectionFromMd(md):
    md_sections = list()
    for i in range(0, md.GetChildNumber()):
        md_sections.append(md.GetChild(i).GetLabel())
    return md_sections


class Timeseries:
    def __init__(self, workingDirectory, modelledC3dfilenames):
        self.workingDirectory = workingDirectory
        self.modelledC3dfilenames = modelledC3dfilenames

        c3dValObj = c3dValidation.c3dValidation(self.workingDirectory)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def calculateTimeseries(self):
        #metaObj = metadata.Metadata(self.workingDirectory)
        timeseries = dict()
        components = {'X', 'Y', 'Z'}
        origLabelNames = list()
        origLabels = {}

        for filename in self.fileNames:  # create list of signals. Make sure that missing signal in one of trial will not break it
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d', '')
            origLabels[measurementName] = {}
            origLabelNamesSelected = list()

            acq = qtools.fileOpen(filename)
            md = acq.GetMetaData()

            if "PROCESSING" in _getSectionFromMd(md):
                processingMd = acq.GetMetaData().FindChild("PROCESSING").value()

                if "Weight" in _getSectionFromMd(processingMd):
                    mass = processingMd.FindChild(
                        "Weight").value().GetInfo().ToString()

                elif "Bodymass" in _getSectionFromMd(processingMd):
                    mass = processingMd.FindChild(
                        "Bodymass").value().GetInfo().ToString()

            noMarkers = range(acq.GetPointNumber())

            for number in noMarkers:
                marker = acq.GetPoint(number)
                origLabelNames.append(marker.GetLabel())

            for origLabelName in origLabelNames:
                if origLabelName in signalMapping.sigNameMap and signalMapping.sigNameMap.get(origLabelName) is not "":
                    origLabelNamesSelected.append(origLabelName)

            origLabels[measurementName] = origLabelNamesSelected

        for origLabelNameSelected in origLabelNamesSelected:
            if signalMapping.sigNameMap.get(origLabelNameSelected) is not "":
                ourSigName = signalMapping.sigNameMap.get(
                    origLabelNameSelected)

                for component in components:
                    timeseries[ourSigName + "_" + component] = {}

                    for filename in self.fileNames:
                        acq = qtools.fileOpen(filename)
                        measurementName = path.basename(filename)
                        measurementName = measurementName.replace('.c3d', '')

                        if component == "X":
                            i = 0
                        elif component == "Y":
                            i = 1
                        elif component == "Z":
                            i = 2
                        bodyMass = float(mass[0])
                        constant2 = 0
                        if "Moment" in ourSigName:
                            constant1 = 1000  # converts from mm to m
                        elif "GRF" in ourSigName:
                            if component == "X":
                                i = 1
                                constant1 = bodyMass * 9.81 * -1
                            elif component == "Y":
                                i = 0
                                constant1 = bodyMass * 9.81 * -1
                            else:
                                constant1 = bodyMass * 9.81
                        elif "Ankle Angles" in ourSigName and component == "Y":
                            constant1 = -1
                        elif "Prog" in ourSigName and component == "X":
                            constant1 = - 1
                            constant2 = -90
                        else:
                            constant1 = 1

                        if "Power" in ourSigName:
                            i = 2

                        if origLabelNameSelected in origLabels[measurementName]:
                            marker = acq.GetPoint(origLabelNameSelected)
                            values = (np.array(marker.GetValues()[
                                      :, i]) / constant1) + constant2
                            timeseries[ourSigName + "_" +
                                       component][measurementName] = {}
                            timeseries[ourSigName + "_" +
                                       component][measurementName] = values
        return timeseries
