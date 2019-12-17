# -*- coding: utf-8 -*-

from pyCGM2 import btk
import signalMapping
from os import listdir, path
import numpy as np
import scipy.signal

null = None

#File management
def fileOpen(filename):
    reader = btk.btkAcquisitionFileReader() # build a btk reader object
    reader.SetFilename(filename) # set a filename to the reader
    reader.Update()
    acq = reader.GetOutput() # acq is the btk aquisition object
    return acq

def createC3dFileList(workingDirectory):
    c3dFileList = list()
    for file in listdir(workingDirectory):
        if file.endswith(".c3d"):
            c3dFileList.append(path.join(workingDirectory, file))
    return c3dFileList

#Signal manamegent
def renameSignal(array,signame):
    out = str(array.get(signame))
    return out

#Export to json
def setEventData(eventData,measurementNames,eventName):
    out = list()
    for measurementName in measurementNames:
        keyName = measurementName + "_" + eventName
        if keyName in eventData:
            out.append(eventData[measurementName + "_" + eventName])
    return out

def loadEvents(eventLabels,eventsDict):
    e = list()
    for label in eventLabels:
        e.append(eventsDict[label])
    return e

#Events
def groupEvents(acq,measurementName,unit):
    eventLabels = list()
    eventsGroupped = dict()
    eventTimesLHS = list()
    eventTimesRHS = list()
    eventTimesLTO = list()
    eventTimesRTO = list()

    noEvents = range(acq.GetEventNumber())
    frameRate = acq.GetPointFrequency()

    for number in noEvents:
        firstFrame = acq.GetFirstFrame()
        event = acq.GetEvent(number) # extract the event of the aquisition
        eventFrame = event.GetFrame()
        eventFrameCropped = eventFrame - firstFrame
        eventTime = eventFrameCropped / frameRate

        if unit == "time":
            eventUn = eventTime
        elif unit == "frames":
            eventUn = eventFrameCropped

        eventName = event.GetLabel()
        eventSide = event.GetContext() # return a string representing the Context
        eventLabelOrig = eventSide + " " + eventName
        eventLabel = renameSignal(signalMapping.eventNameMap,eventLabelOrig)

        if eventLabel not in eventLabels:
            eventLabels.append(eventLabel)

        if eventLabel == "LHS":
            eventTimesLHS.append(eventUn)
            eventTimesLHS.sort()
            eventsGroupped[measurementName + "_" + eventLabel] = eventTimesLHS
        elif eventLabel == "RHS":
            eventTimesRHS.append(eventUn)
            eventTimesRHS.sort()
            eventsGroupped[measurementName + "_" + eventLabel] = eventTimesRHS
        elif eventLabel == "LTO":
            eventTimesLTO.append(eventUn)
            eventTimesLTO.sort()
            eventsGroupped[measurementName + "_" + eventLabel] = eventTimesLTO
        elif eventLabel == "RTO":
            eventTimesRTO.append(eventUn)
            eventTimesRTO.sort()
            eventsGroupped[measurementName + "_" + eventLabel] = eventTimesRTO
    return eventsGroupped

def timeBetweenEvents(measurementName,events,event1,event2):
    a = events[measurementName + "_" + event1]
    b = events[measurementName + "_" + event2]

    aa = np.sort(np.array(a))
    bb = np.sort(np.array(b))

    n = np.argmax(bb > aa.item(0))

    if n > 0:
        bb = np.delete(bb,n-1)

    aaLen = np.size(aa)
    bbLen = np.size(bb)
    index = np.arange(bbLen, aaLen)
    index.tolist()

    if aaLen > bbLen:
        aa = np.delete(aa,index)

    c = list(np.abs(aa - bb))
    return c


#Signal Processing
def signalValueAtEvent(eventList, signal, eventName):
    for key, value in eventList.iteritems():
        if eventName in key:
            value2 = np.array(value)
            out = signal[value2]
    return out

def firstDerivative (signal, capture_rate):
    sig_vel = np.diff(signal) / (1/capture_rate)
    return sig_vel

def filterButter (signame, capture_rate, order, fiter_fq, filterType):
    b, a = scipy.signal.butter(order, fiter_fq/(0.5*capture_rate), filterType)
    sig_filtered = scipy.signal.filtfilt(b, a, signame)
    return sig_filtered

def globalMax(signame):
    max = np.nanmax(signame)
    return max

def timeGlobalMax(signame, capture_rate, unit):
    frame_of_max = signame.argmax()
    time_of_max = frame_of_max / capture_rate
    if unit == "time":
        max = time_of_max
    elif unit == "frame":
        max = frame_of_max
    return max

def rootMeanSquared(sig):
    mean= np.mean(sig)
    mse = np.sum(np.power(sig - mean,2))/101
    rms = np.sqrt(mse)
    return rms

def getKeyNameList(dictionary):
    return list(dictionary.keys())

def getSeriesValuesExport(signalData, signalName, precision, frameRate):
    exportFormatData = []
    for trialName, trialData in signalData.items():
        trialData = np.round(trialData,precision).tolist()
        if trialData is not "":
            exportFormatData.append({"measurement": trialName,
                    "values": trialData,
                    "rate": frameRate})
    return exportFormatData

def getSeriesExport(signalData, signalName, dataType, precision, frameRate, path):

    if signalName.startswith('Left'):
        sideSet = 'left'
    elif signalName.startswith('Right'):
        sideSet = 'right'
    else:
        sideSet = null

    return {
       "id": signalName,
       "type": dataType,
       "set": sideSet,
       "path": path,
       "data": getSeriesValuesExport(signalData,signalName, precision, frameRate)
       }

def isPointExist(acq,label):
    i = acq.GetPoints().Begin()
    while i != acq.GetPoints().End():
        if i.value().GetLabel()==label:
            flag = True
            break
        else:
            i.incr()
            flag = False

    if flag:
        return True
    else:
        return False

#a = getSeriesValuesExport(b, 'Left Ankle Angles_X', 4, 100)
#d = getSeriesExport(b ,('20141105-GBNNN-VDEF-16','20141105-GBNNN-VDEF-07'), 'Left Ankle Angles_X', 'series', 4, 100)
