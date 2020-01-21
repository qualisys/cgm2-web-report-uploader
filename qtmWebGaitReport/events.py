# -*- coding: utf-8 -*-

import qtools
import signalMapping
from os import path
import c3dValidation
import numpy as np


class Events:
    def __init__(self, workingDirectory):
        self.workingDirectory = workingDirectory

        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def calculateEvents(self):
        eventLabels = dict()
        eventsGroupped = dict()
        eventData = dict()
        null = None

        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)

            measurementName = path.basename(filename)
            measurementName = measurementName.replace('.c3d', '')

            eventLabels[measurementName] = []

            frameRate = acq.GetPointFrequency()

            noEvents = range(acq.GetEventNumber())
            eventTimesLHS = list()
            eventTimesRHS = list()
            eventTimesLTO = list()
            eventTimesRTO = list()

            for number in noEvents:
                firstFrame = acq.GetFirstFrame()
                lastFrame = acq.GetLastFrame()
                # extract the event of the aquisition
                event = acq.GetEvent(number)
                eventFrame = event.GetFrame() - firstFrame
                eventTime = eventFrame / frameRate
                eventName = event.GetLabel()
                eventSide = event.GetContext()  # return a string representing the Context
                eventLabelOrig = eventSide + " " + eventName
                eventLabel = qtools.renameSignal(
                    signalMapping.eventNameMap, eventLabelOrig)

                if eventLabel not in eventLabels[measurementName] and eventLabel != 'None':
                    eventLabels[measurementName].append(eventLabel)

                if eventLabel == "LHS":
                    eventTimesLHS.append(eventTime)
                    eventsGroupped[measurementName +
                                   "_" + eventLabel] = eventTimesLHS
                    if self.checkSignalExists(acq, measurementName, 'LGroundReactionForce'):
                        eventTimeLON = self.getOnOffEvent(
                            acq, measurementName, 'LGroundReactionForce', frameRate, firstFrame, lastFrame, eventFrame, eventTime, 'on')
                        if eventTimeLON:
                            eventsGroupped[measurementName +
                                           "_LON"] = eventTimeLON
                            eventLabels[measurementName].append('LON')
                elif eventLabel == "RHS":
                    eventTimesRHS.append(eventTime)
                    eventsGroupped[measurementName +
                                   "_" + eventLabel] = eventTimesRHS
                    if self.checkSignalExists(acq, measurementName, 'RGroundReactionForce'):
                        eventTimeRON = self.getOnOffEvent(
                            acq, measurementName, 'RGroundReactionForce', frameRate, firstFrame, lastFrame, eventFrame, eventTime, 'on')
                        if eventTimeRON:
                            eventsGroupped[measurementName +
                                           "_RON"] = eventTimeRON
                            eventLabels[measurementName].append('RON')
                elif eventLabel == "LTO":
                    eventTimesLTO.append(eventTime)
                    eventsGroupped[measurementName +
                                   "_" + eventLabel] = eventTimesLTO
                    if self.checkSignalExists(acq, measurementName, 'LGroundReactionForce'):
                        eventTimeLOFF = self.getOnOffEvent(
                            acq, measurementName, 'LGroundReactionForce', frameRate, firstFrame, lastFrame, eventFrame, eventTime, 'off')
                        if eventTimeLOFF:
                            eventsGroupped[measurementName +
                                           "_LOFF"] = eventTimeLOFF
                            eventLabels[measurementName].append('LOFF')
                elif eventLabel == "RTO":
                    eventTimesRTO.append(eventTime)
                    eventsGroupped[measurementName +
                                   "_" + eventLabel] = eventTimesRTO
                    if self.checkSignalExists(acq, measurementName, 'RGroundReactionForce'):
                        eventTimeROFF = self.getOnOffEvent(
                            acq, measurementName, 'RGroundReactionForce', frameRate, firstFrame, lastFrame, eventFrame, eventTime, 'off')
                        if eventTimeROFF:
                            eventsGroupped[measurementName +
                                           "_ROFF"] = eventTimeROFF
                            eventLabels[measurementName].append('ROFF')

            for eventLabel in eventLabels[measurementName]:
                eventData[measurementName + "_" + eventLabel] = {
                    "measurement": measurementName,
                    "values": eventsGroupped[measurementName + "_" + eventLabel],
                    "rate": null
                }
        return (eventData, eventLabels)

    def checkSignalExists(self, acq, measurementName, GRFSignalName):
        try:
            signal = acq.GetPoint(GRFSignalName)
        except:
            print(measurementName + " " + GRFSignalName + ' signal is missing')
            out = False
        else:
            out = True
        return out

    def getOnOffEvent(self, acq, measurementName, GRFSignalName, frameRate, firstFrame, lastFrame, eventFrame, eventTime, eventType):
        out = []
        if self.checkSignalExists(acq, measurementName, GRFSignalName):
            # read corresponding GRF signal
            signal = acq.GetPoint(GRFSignalName)
            value = np.array(signal.GetValues()[:, 2])
            frameCheckBefore = int(eventFrame - round(frameRate/10, 0))
            frameCheckAfter = int(eventFrame + round(frameRate/10, 0))

            if value.shape[0] < frameCheckAfter:
                frameCheckAfter = value.shape[0] - 1

            if frameCheckBefore < 0:
                frameCheckBefore = 0

            if eventType == 'on' and value[frameCheckBefore] < 0.1 and value[frameCheckAfter] > 0.1:
                out.append(eventTime)
            elif eventType == 'off' and value[frameCheckBefore] > 0.1 and value[frameCheckAfter] < 0.1:
                out.append(eventTime)
            return out
