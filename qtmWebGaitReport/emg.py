# -*- coding: utf-8 -*-
from os import path

import numpy as np

from qtmWebGaitReport import c3dValidation, qtools, signalMapping


class EMG:
    def __init__(self, workingDirectory):
        self.workingDirectory = workingDirectory

        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def calculateRawEMG(self):
        origEMGNames = list()
        emgData = {}

        noSignals = 0
        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            noSignals = acq.GetAnalogNumber()

        for number in range(noSignals):  # it is assumed same signals are in all trials
            signal = acq.GetAnalog(number)
            signalLabel = signal.GetLabel()

            if "Moment" not in signalLabel and "Force" not in signalLabel:
                origEMGNames.append(signal.GetLabel())

        for origSigName, ourSigName in signalMapping.emgNameMap.iteritems():
            if origSigName in origEMGNames and ourSigName is not "":
                emgData[ourSigName] = {}

                for filename in self.fileNames:
                    acq = qtools.fileOpen(filename)
                    measurementName = path.basename(filename)
                    measurementName = measurementName.replace(".c3d", "")

                    signal = acq.GetAnalog(origSigName)
                    values = np.array(signal.GetValues()[:, 0])

                    emgData[ourSigName][measurementName] = {}
                    emgData[ourSigName][measurementName] = values

        return emgData

    def calculateProcessedEMG(self, analogRate, hiBiPass, lowBiPass, hiCutoff, lowCutoff, RMSwindow):
        rawSigs = self.calculateRawEMG()
        sig = {}
        for key, value in rawSigs.iteritems():
            sig[key] = {}
            for key2, value2 in value.iteritems():
                sig[key][key2] = {}

                # Highpass, cutoff 10, bidirect 1
                sig[key][key2] = qtools.filterButter(value2, analogRate, hiBiPass, hiCutoff, "highpass")

                # RMS, window 100
                sig[key][key2] = self.movingRMS(sig[key][key2], RMSwindow)
        return sig

    def movingRMS(self, sig, windowSize):
        sig2 = np.power(sig, 2)
        window = np.ones(windowSize) / float(windowSize)
        return np.sqrt(np.convolve(sig2, window, "valid"))
