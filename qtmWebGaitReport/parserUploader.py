# -*- coding: utf-8 -*-
import qtools
import timeseries
import events
import map2
import emg
import metadata
import tsp
import measurements
import avi2mp4
import requests
import c3dValidation
import json
from os import path, getcwd
import webbrowser


class ParserUploader:
    def __init__(self, workingDirectory, configData, modelledC3dfilenames, subjectMetadata, sessionDate):
        self.workingDirectory = workingDirectory
        self.configData = configData
        self.modelledC3dfilenames = modelledC3dfilenames
        self.subjectMetadata = subjectMetadata
        self.creationDate = sessionDate

    def createReportJson(self):
        c3dValObj = c3dValidation.c3dValidation(self.workingDirectory)

        measurementNames = []
        fileNames = []
        for filename in self.modelledC3dfilenames:
            measurementNames.append(str(filename[:-4]))
            fileNames.append(
                str(path.join(self.workingDirectory, filename)))
        # measurementNames = c3dValObj.getValidC3dList(True)
        # fileNames = c3dValObj.getValidC3dList(False)
        eventsDict = dict()
        null = None

        if fileNames:  # empty list means c3d does not contain Plugin-Gait created 'LAnkleAngles' or there are no events
            for filename in fileNames:
                acq = qtools.fileOpen(filename)

                frameRate = acq.GetPointFrequency()
                analogRate = acq.GetAnalogFrequency()

            # Timeseries
            tsObj = timeseries.Timeseries(
                self.workingDirectory, self.modelledC3dfilenames)
            tseries = tsObj.calculateTimeseries()
            sigList = qtools.getKeyNameList(tseries)

            ts = list()
            for sig in sigList:
                ts.append(qtools.getSeriesExport(tseries, measurementNames,
                                                 sig, "series", 4, frameRate, "LINK_MODEL_BASED/ORIGINAL"))

            print "--------------------Timeseries OK--------------------------------"
            # GVS
            mapProfile = map2.MAP(self.workingDirectory)
            gvsScore = mapProfile.calculateGVS()[1]
            sigList = qtools.getKeyNameList(gvsScore)

            gvs = list()
            for sig in sigList:
                gvs.append(qtools.getSeriesExport(
                    gvsScore, measurementNames, sig, "scalar", 4, null, "LINK_MODEL_BASED/ORIGINAL"))

            print "--------------------GVS OK--------------------------------"

            # GPS
            gpsScoreLeft = mapProfile.calculateGPS()[0]
            gpsScoreRight = mapProfile.calculateGPS()[1]
            gpsScoreOverall = mapProfile.calculateGPS()[2]

            gpsLeft = mapProfile.gpsExport(
                gpsScoreLeft, "Left_GPS_ln_mean", frameRate)
            gpsRight = mapProfile.gpsExport(
                gpsScoreRight, "Right_GPS_ln_mean", frameRate)
            gpsOverall = mapProfile.gpsExport(
                gpsScoreOverall, "Overall_GPS_ln_mean", frameRate)
            gps = gpsLeft + gpsRight + gpsOverall

            print "--------------------GPS OK--------------------------------"

            # EMG
            emgObj = emg.EMG(self.workingDirectory)
            emgData = emgObj.calculateRawEMG()
            sigList = qtools.getKeyNameList(emgData)

            emgExp = list()
            for sig in sigList:
                emgExp.append(qtools.getSeriesExport(
                    emgData, measurementNames, sig, "series", 8, analogRate, "ANALOG/EMG_RAW_web"))

            print "--------------------EMG--------------------------------"

            # Events
    #        noMeasurements = range(len(measurementNames))
            eventsObj = events.Events(self.workingDirectory)
            eventData = eventsObj.calculateEvents()[0]
            eventLabels = eventsObj.calculateEvents()[1]

            maxNumEvents = 0
            for measurementName in measurementNames:
                numEvents = len(eventLabels[measurementName])
                if numEvents > maxNumEvents:
                    maxEventList = eventLabels[measurementName]

            for label in maxEventList:
                set = ""
                if label.lower().startswith("l"):
                    set = "left"
                else:
                    set = "right"

                eventsDict[label] = {"id": label,
                                     "set": set,
                                     "data": qtools.setEventData(eventData, measurementNames, label)
                                     }

            ev = qtools.loadEvents(maxEventList, eventsDict)

            print "--------------------events OK--------------------------------"
            # root = {
            #         "results": ts + gvs + gps + emgExp,
            #         "events": ev,
            #         "clientId": self.configData["clientId"],
            #         }

            # #MetaData
            metaDataObj = metadata.Metadata(
                self.workingDirectory, self.modelledC3dfilenames, self.subjectMetadata, self.creationDate)
            md = metaDataObj.medatadaInfo()
            print "--------------------metadata OK--------------------------------"

            # Subject
            sub = metaDataObj.subjectInfo()
            print "--------------------subjectInfo OK--------------------------------"
            # Project
            proj = metaDataObj.projectInfo()
            print "--------------------proj OK--------------------------------"

            # TSP
            tspObj = tsp.TSP(self.workingDirectory)
            tsparams = tspObj.export()
            print "--------------------TSP OK--------------------------------"
            #
            #
            # Measurements
            measObj = measurements.Measurements(self.workingDirectory)
            mea = measObj.measurementInfo()

            print "--------------------Measurements OK--------------------------------"

            # Create json
            root = {
                "results": ts + gvs + gps + emgExp + tsparams,
                "events": ev,
                "metadata": md,
                "measurements": mea,
                "clientId": self.configData["clientId"],
                "subject": sub,
                "project": proj
            }

            return root
        else:
            root = []
            return root

    def Upload(self):
        # Convert Avi to mp4
        videoObj = avi2mp4.AviToMp4(self.workingDirectory)
        videoObj.convertAviToMp4()

        # check that clientId, baseUrl and token are specified in config.json
        if "clientId" in self.configData.keys():
            clientIdExists = True
        else:
            clientIdExists = False
            print "Error: Specify clientID in config.json"

        if "baseUrl" in self.configData.keys():
            baseUrlExists = True
        else:
            baseUrlExists = False
            print "Error: Specify baseUrl in config.json"

        # Upload
        reportData = self.createReportJson()

        if clientIdExists and baseUrlExists:  # and tokenExists:
            if reportData:
                baseUrl = self.configData["baseUrl"]

                # Get upload token
                from temp import get_upload_token
                uploadToken = get_upload_token(
                    self.configData["baseUrl"], self.configData["clientId"])
                headers = {'Authorization': 'Bearer ' + uploadToken}

                reportReq = requests.post(
                    baseUrl + '/api/v2/report/', json=reportData, headers=headers)
                if reportReq.status_code != 200:
                    print(reportReq.status_code)
                    print(reportReq.text)
                    raise Exception(
                        "Posting report data returned with a status code != 200, status code {code},\n response text {text}".format(code=reportReq.status_code, text=reportReq.text))
                reportResJson = reportReq.json()
                newReportId = reportResJson['id']

                resourceOutput = videoObj.getMp4Filenames(False)

                for index, resource in enumerate(resourceOutput):
                    fileData = {'file_' + `index`: open(resource, 'rb')}
                    resourceReq = requests.post(
                        baseUrl + '/api/v2/report/' + newReportId + '/resource', files=fileData, headers=headers)
                print "Report [%s] generated" % (str(newReportId))
                webbrowser.open_new_tab(baseUrl + '/claim/' + newReportId)
            else:
                print "Error: No c3d file found that has been processed with Plugin-Gait."
