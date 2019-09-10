# -*- coding: utf-8 -*-
import qtools
from os import path
import numpy as np
import signalMapping
import c3dValidation

#workingDirectory = "E:\\Qualisys_repository\\Gait-Web-Importer\\Data\\myMess\\"

class EMG:
    def __init__(self,workingDirectory):
        self.workingDirectory = workingDirectory
        
        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def calculateRawEMG(self):
        origEMGNames = list()
        emgData = {}
        
        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            noSignals = range(acq.GetAnalogNumber())
            
        for number in noSignals: #it is assumed same signals are in all trials
            signal = acq.GetAnalog(number)
            signalLabel = signal.GetLabel()
            
            if "Moment" not in signalLabel and "Force" not in signalLabel:
                origEMGNames.append(signal.GetLabel())

        for origSigName, ourSigName in signalMapping.emgNameMap.iteritems():
            if origSigName in origEMGNames and ourSigName is not "":
                emgData[ourSigName] = {}
#                emgData[ourSigName + "_raw"] = {}

                for filename in self.fileNames:
                    acq = qtools.fileOpen(filename)
                    measurementName = path.basename(filename)
                    measurementName = measurementName.replace('.c3d','')

                    signal = acq.GetAnalog(origSigName)
                    values = np.array(signal.GetValues()[:,0])
#                    values_list = [round(elem,4) for elem in values_list]
                    
                    emgData[ourSigName][measurementName] = {}                     
                    emgData[ourSigName][measurementName] = values
#                    emgData[ourSigName + "_raw"][measurementName] = {}                     
#                    emgData[ourSigName + "_raw"][measurementName] = values
                        
        return emgData

    def calculateProcessedEMG(self,analogRate, hiBiPass, lowBiPass, hiCutoff, lowCutoff, RMSwindow):
        rawSigs = self.calculateRawEMG()
        sig = {}
        for key, value in rawSigs.iteritems():
            sig[key] = {}
            for key2, value2 in value.iteritems():
                sig[key][key2] = {}
            
                #Highpass, cutoff 10, bidirect 1
                sig[key][key2] = qtools.filterButter(value2, analogRate, hiBiPass, hiCutoff, 'highpass')
            
                #Lowwpass (optional), off by default, cuttoff 6?, bidirect 1
                #sig[key][key2] = qtools.filterButter(sig[key][key2], analogRate, lowBiPass, lowCutoff, 'lowpass')
            
                #Rectify (optional) off by default
                #sig[key][key2] = np.abs(sig[key][key2])
            
                #RMS, window 100
                sig[key][key2] = self.movingRMS(sig[key][key2],RMSwindow)
        return sig

    def movingRMS(self,sig, windowSize):
      sig2 = np.power(sig,2)
      window = np.ones(windowSize)/float(windowSize)
      return np.sqrt(np.convolve(sig2, window, 'valid'))

#a = EMG(workingDirectory)
#b = a.calculateProcessedEMG(1000,1,1,10,6,100)

#import matplotlib.pyplot as plt
#plt.plot(b["Right Gastrocnemius"]["Walk01"])
#plt.ylabel('some numbers')
#plt.show()
#
#print b