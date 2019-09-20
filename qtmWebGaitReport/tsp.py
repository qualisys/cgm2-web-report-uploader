# -*- coding: utf-8 -*-

import qtools
from os import path
import numpy as np
import c3dValidation

#workingDirectory = "E:\\OneDrive\\qualisys.se\\App Team - Documents\\Projects\\Gait web reports from Vicon c3d data\\Python parser\\Data\\Oxford\\"

class TSP:
    def __init__(self,workingDirectory):
        self.workingDirectory = workingDirectory
        self.measurementNames = []
        self.null = None

        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.measurementNames = c3dValObj.getValidC3dList(True)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def stepTime(self):
        leftStepTime = list()
        rightStepTime = list()

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = filename.replace('.c3d','')
            measurementName = measurementName.replace(self.workingDirectory,'')

            events = qtools.groupEvents(acq,measurementName,"time")

            leftStepTime.append ({"measurement":measurementName,
                                 "values": qtools.timeBetweenEvents(measurementName,events,"LHS", "RHS")
                                 })
            rightStepTime.append ({"measurement":measurementName,
                                 "values": qtools.timeBetweenEvents(measurementName,events,"RHS", "LHS")
                                 })
        return (leftStepTime,rightStepTime)

    def doubleLimbSupport(self):
        leftDoubleSupport = []
        rightDoubleSupport = []

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            events = qtools.groupEvents(acq,measurementName,"time")

            leftDoubleSupport.append ({"measurement":measurementName,
                                 "values": qtools.timeBetweenEvents(measurementName,events,"LHS", "RTO")
                                 })
            rightDoubleSupport.append ({"measurement":measurementName,
                                 "values": qtools.timeBetweenEvents(measurementName,events,"RHS", "LTO")
                                 })
        return (leftDoubleSupport,rightDoubleSupport)

    def strideTime(self):
        leftStrideTime = dict()
        rightStrideTime = dict()

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            events = qtools.groupEvents(acq,measurementName,"time")

            leftStrideTime[measurementName] = qtools.timeBetweenEvents(measurementName,events,"LHS", "LHS")
            rightStrideTime[measurementName] = qtools.timeBetweenEvents(measurementName,events,"RHS", "RHS")

        return (leftStrideTime,rightStrideTime)

    def stanceTimePct(self):
#        leftCycleTime = dict()
#        rightCycleTime = dict()
        leftStanceTime = dict()
        rightStanceTime = dict()
        leftStanceTimePctD = dict()
        rightStanceTimePctD = dict()
        leftStanceTimePct = list()
        rightStanceTimePct = list()


        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            events = qtools.groupEvents(acq,measurementName,"time")

#            leftCycleTime[measurementName] = qtools.timeBetweenEvents(measurementName,events,"LHS", "LHS")
#            rightCycleTime[measurementName] = qtools.timeBetweenEvents(measurementName,events,"RHS", "RHS")
            leftStanceTime[measurementName] = qtools.timeBetweenEvents(measurementName,events,"LHS", "LTO")
            rightStanceTime[measurementName] = qtools.timeBetweenEvents(measurementName,events,"RHS", "RTO")


            left_stride_number = len(self.strideTime()[0][measurementName])
            right_stride_number = len(self.strideTime()[1][measurementName])

            leftStanceTimePctD[measurementName] = list(np.array(leftStanceTime[measurementName][0:left_stride_number]) / np.array(self.strideTime()[0][measurementName]) * 100) #ISSUE FOUND OUT in native Code.
            rightStanceTimePctD[measurementName] = list(np.array(rightStanceTime[measurementName][0:right_stride_number]) / np.array(self.strideTime()[1][measurementName]) * 100)
#            leftStanceTimePctD[measurementName] = list(np.array(leftStanceTime[measurementName]) / np.array(leftCycleTime[measurementName]) * 100)
#            rightStanceTimePctD[measurementName] = list(np.array(rightStanceTime[measurementName]) / np.array(rightCycleTime[measurementName]) * 100)


            leftStanceTimePct.append ({"measurement":measurementName,
                                 "values": leftStanceTimePctD[measurementName]
                                 })
            rightStanceTimePct.append ({"measurement":measurementName,
                                 "values": rightStanceTimePctD[measurementName]
                                 })


        return (leftStanceTimePct,rightStanceTimePct)

    def cadence(self):
        cadence = []

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            events = qtools.groupEvents(acq,measurementName,"time")

            leftStepT = np.array(qtools.timeBetweenEvents(measurementName,events,"LHS", "RHS"))
            rightStepT = np.array(qtools.timeBetweenEvents(measurementName,events,"RHS", "LHS"))
            stepTime = np.append(leftStepT,rightStepT)

            cadence.append ({"measurement":measurementName,
                                 "values": list(60 / stepTime)
                                 })
        return cadence

    def strideLength(self):
        leftStrideLength = list()
        rightStrideLength = list()
        leftFootAtLHS = dict()
        rightFootAtRHS = dict()

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            eventsFr = qtools.groupEvents(acq,measurementName,"frames")

            leftFootProx = acq.GetPoint("LHEE") #to do: decide what marker/landmark to use
#            leftFootProx = acq.GetPoint("LPROXFF")
            leftFootProxValues = leftFootProx.GetValues()
            rightFootProx = acq.GetPoint("RHEE")
#            rightFootProx = acq.GetPoint("RPROXFF")
            rightFootProxValues = rightFootProx.GetValues()
            leftFootAtLHS[measurementName] = qtools.signalValueAtEvent(eventsFr,leftFootProxValues,"LHS")
            rightFootAtRHS[measurementName] = qtools.signalValueAtEvent(eventsFr,rightFootProxValues,"RHS")

            leftStrideLength.append ({"measurement":measurementName,
                                 "values": self.prepStrideLength(leftFootAtLHS[measurementName])
                                 })
            rightStrideLength.append ({"measurement":measurementName,
                                 "values": self.prepStrideLength(rightFootAtRHS[measurementName])
                                 })

        return (leftStrideLength,rightStrideLength,leftFootAtLHS,rightFootAtRHS)

    def prepStrideLength(self,instances):
        strideLength = list()
        noCol = instances.shape
        rr = int(noCol[0]) - 1

        i = 0
        while i < rr:
            j = i + 1
            firstInstance =  instances[i][1] / 1000
            secondInstance =  instances[j][1] / 1000
            i = i + 1

            strideLength.append(np.abs(firstInstance - secondInstance))
        return strideLength

    def strideWidth(self):
        strideWidth = list()

        for filename in self.fileNames:
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')

            lfAtLHS = np.array(self.strideLength()[2][measurementName])
            rfAtRHS = np.array(self.strideLength()[3][measurementName])

            lfAtLHSLen = len(lfAtLHS)
            rfAtRHSLen = len(rfAtRHS)

            if rfAtRHSLen > lfAtLHSLen: #assumes no HS is missing in step sequence
                n = rfAtRHSLen - lfAtLHSLen
                rfAtRHS = rfAtRHS[:-n,:]
            if lfAtLHSLen > rfAtRHSLen: #assumes no HS is missing in step sequence
                n = lfAtLHSLen - rfAtRHSLen
                lfAtLHS = lfAtLHS[:-n,:]

            strideW = (lfAtLHS - rfAtRHS) / 1000
            strideWidth.append ({"measurement":measurementName,
                                 "values": list(np.abs(strideW[:,0]))
                                 })
        return strideWidth

    def stepLength(self):
        leftStepLength = list()
        rightStepLength = list()

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d','')
            eventsFr = qtools.groupEvents(acq,measurementName,"frames")

            lfatLHS = np.array(self.strideLength()[2][measurementName])
            rfatRHS = np.array(self.strideLength()[3][measurementName])

            leftStepLength.append ({"measurement":measurementName,
                                 "values": self.prepStepLength(eventsFr,measurementName,lfatLHS,rfatRHS)[0]
                                 })
            rightStepLength.append ({"measurement":measurementName,
                                 "values": self.prepStepLength(eventsFr,measurementName,lfatLHS,rfatRHS)[1]
                                 })
        return (leftStepLength,rightStepLength)

    def prepStepLength(self,eventsFr, measurementName,leftFootAtLHS,rightFootAtRHS):
        leftStepLength = dict()
        rightStepLength = dict()

        for key, value in eventsFr.iteritems():
            leftStepL = list()
            rightStepL = list()

            if "LHS" in key:
                LHSCount = len(eventsFr[measurementName + "_LHS"])
                LHSFirst = value[0]
            elif "RHS" in key:
                RHSCount = len(eventsFr[measurementName + "_RHS"])
                RHSFirst = value[0]

        if LHSFirst < RHSFirst:
            for i in range(LHSCount - 1):
                heelStrike1 = leftFootAtLHS[i,1]
                heelStrike2 = rightFootAtRHS[i,1]
                heelStrike3 = leftFootAtLHS[i + 1,1]
                rightStepL.append(heelStrike2 - heelStrike1)
                leftStepL.append(heelStrike3 - heelStrike2)

        if LHSFirst > RHSFirst:
            for i in range(RHSCount - 1):
                heelStrike1 = rightFootAtRHS[i,1]
                heelStrike2 = leftFootAtLHS[i,1]
                heelStrike3 = rightFootAtRHS[i + 1,1]
                leftStepL.append(heelStrike2 - heelStrike1)
                rightStepL.append(heelStrike3 - heelStrike2)

        leftStepLength[measurementName] = list(np.abs(leftStepL) / 1000)
        rightStepLength[measurementName] = list(np.abs(rightStepL) / 1000)

        return [leftStepLength[measurementName],rightStepLength[measurementName]]

#    def speed(self):
#       speed = {}
#
#       for filename in self.fileNames:
#            acq = qtools.fileOpen(filename)
#            measurementName = path.basename(filename)
#            measurementName = measurementName.replace('.c3d','')
#
#            speed[measurementName] = {}
#            speed[measurementName] = self.strideLength()[0]
#
#       return speed

    def export(self):
        exp = [          {"id": "Left_Step_Time",
                         "set": "left",
                         "type": "scalar",
                         "data": self.stepTime()[0]},
                        {"id": "Right_Step_Time",
                         "set": "right",
                         "type": "scalar",
                         "data": self.stepTime()[1]},
                        {"id": "Left_Initial_Double_Limb_Support_Time",
                         "set": "left",
                         "type": "scalar",
                         "data":  self.doubleLimbSupport()[0]},
                        {"id": "Right_Initial_Double_Limb_Support_Time",
                         "set": "right",
                         "type": "scalar",
                         "data":  self.doubleLimbSupport()[1]},
                        {"id": "Left_Stance_Time_Pct",
                         "set": "left",
                         "type": "scalar",
                         "data":  self.stanceTimePct()[0]},
                        {"id": "Right_Stance_Time_Pct",
                         "set": "right",
                         "type": "scalar",
                         "data":  self.stanceTimePct()[1]},
                        {"id": "Cadence",
                         "set": self.null,
                         "type": "scalar",
                         "data":  self.cadence()},
                        {"id": "Stride_Length",
                         "set": self.null,
                         "type": "scalar",
                         "data": self.strideLength()[0]},
                        {"id": "Stride_Width",
                         "set": self.null,
                         "type": "scalar",
                         "data":  self.strideWidth()},
                        {"id": "Left_Step_Length",
                         "set": "left",
                         "type": "scalar",
                         "data":  self.stepLength()[0]},
                        {"id": "Right_Step_Length",
                         "set": "right",
                         "type": "scalar",
                         "data":  self.stepLength()[1]},

                ]
        return exp

#a = TSP(workingDirectory)
#b = a.strideLength()
#print b
