# -*- coding: utf-8 -*-
from qtmWebGaitReport import qtools
from qtmWebGaitReport import timeseries
from qtmWebGaitReport import events
from qtmWebGaitReport import map2
from qtmWebGaitReport import emg
from qtmWebGaitReport import metadata
from qtmWebGaitReport import tsp
from qtmWebGaitReport import measurements
from qtmWebGaitReport.avi2mp4 import get_mp4_filepaths
from qtmWebGaitReport.avi2mp4 import get_parent_folder_absolute_path
import requests
from qtmWebGaitReport import c3dValidation
import webbrowser


def getFrameAndAnalogRateFromC3D(filePath):
    acq = qtools.fileOpen(filePath)

    frameRate = acq.GetPointFrequency()
    analogRate = acq.GetAnalogFrequency()
    return frameRate, analogRate


def get_force_threshold_in_newton(settings_from_php):
    if "force_threshold" in settings_from_php.keys():
        force_threshold_newton = settings_from_php["force_threshold"]
    else:
        force_threshold_newton = 10
    return force_threshold_newton


class ReportJsonGenerator:
    def __init__(
        self, workingDirectory, clientId, modelledC3dfilenames, subjectMetadata, sessionDate, extra_settings={}
    ):
        self.workingDirectory = workingDirectory
        self.clientId = clientId
        self.modelledC3dfilenames = modelledC3dfilenames
        self.subjectMetadata = subjectMetadata
        self.creationDate = sessionDate
        self.extra_settings = extra_settings

    def getTimeseriesResults(self):
        tsObj = timeseries.Timeseries(self.workingDirectory, self.modelledC3dfilenames)
        mass = float(self.subjectMetadata["bodyWeight"])
        timeSeriesData = tsObj.calculateTimeseries(mass)
        timeseriesResults = []
        for signalName, signalData in timeSeriesData.items():
            timeseriesResults.append(
                qtools.getSeriesExport(signalData, signalName, "series", 4, self.frameRate, "LINK_MODEL_BASED/ORIGINAL")
            )
        return timeseriesResults

    def getGVSResults(self, mapProfile):
        gvsScore = mapProfile.getAllGVS()

        gvs = []
        for signalName, signalData in gvsScore.items():
            gvs.append(
                qtools.getSeriesExport(signalData, signalName, "scalar", 4, self.null, "LINK_MODEL_BASED/ORIGINAL")
            )
        return gvs

    def getGPSResults(self, mapProfile):
        gpsScoreLeft, gpsScoreRight, gpsScoreOverall = mapProfile.getAllGPS()

        gpsLeft = mapProfile.gpsExport(gpsScoreLeft, "Left_GPS_ln_mean", self.frameRate)
        gpsRight = mapProfile.gpsExport(gpsScoreRight, "Right_GPS_ln_mean", self.frameRate)
        gpsOverall = mapProfile.gpsExport(gpsScoreOverall, "Overall_GPS_ln_mean", self.frameRate)
        return gpsLeft + gpsRight + gpsOverall

    def getEMGResults(self):
        emgObj = emg.EMG(self.workingDirectory)
        emgData = emgObj.calculateRawEMG()

        emgExp = []
        for signalName, signalData in emgData.items():
            emgExp.append(
                qtools.getSeriesExport(signalData, signalName, "series", 8, self.analogRate, "ANALOG/EMG_RAW_web")
            )
        return emgExp

    def getEvents(self):
        eventsObj = events.Events(self.workingDirectory)

        forceThresholdNewton = get_force_threshold_in_newton(self.extra_settings)
        forceThresholdNormalised = forceThresholdNewton / float(self.subjectMetadata["bodyWeight"])  # X Newton / BW kg
        eventData = eventsObj.calculateEvents(forceThresholdNormalised)[0]
        eventLabels = eventsObj.calculateEvents(forceThresholdNormalised)[1]

        maxNumEvents = 0
        maxEventList = []
        for measurementName in self.measurementNames:
            if measurementName in eventLabels.keys():
                numEvents = len(eventLabels[measurementName])
                if numEvents > maxNumEvents:
                    maxEventList = eventLabels[measurementName]
        eventsDict = {}
        for label in maxEventList:
            set = ""
            if label.lower().startswith("l"):
                set = "left"
            else:
                set = "right"

            eventsDict[label] = {
                "id": label,
                "set": set,
                "data": qtools.setEventData(eventData, self.measurementNames, label),
            }

        ev = qtools.loadEvents(maxEventList, eventsDict)
        return ev

    def createReportJson(self):
        c3dValObj = c3dValidation.c3dValidation(self.workingDirectory)

        self.measurementNames = c3dValObj.getValidC3dList(True)
        fileNames = c3dValObj.getValidC3dList(False)
        self.null = None

        if (
            fileNames != []
        ):  # empty list means c3d does not contain Plugin-Gait created 'LAnkleAngles' or there are no events
            self.frameRate, self.analogRate = getFrameAndAnalogRateFromC3D(fileNames[0])

            ts = self.getTimeseriesResults()
            print("--------------------Timeseries OK--------------------------------")
            mapProfile = map2.MAP(self.workingDirectory)
            gvs = self.getGVSResults(mapProfile)
            print("--------------------GVS OK--------------------------------")
            gps = self.getGPSResults(mapProfile)
            print("--------------------GPS OK--------------------------------")
            emgExp = self.getEMGResults()
            print("--------------------EMG--------------------------------")

            # Events
            ev = self.getEvents()

            print("--------------------events OK--------------------------------")

            # #MetaData
            metaDataObj = metadata.Metadata(
                self.workingDirectory, self.modelledC3dfilenames, self.subjectMetadata, self.creationDate
            )
            md = metaDataObj.medatadaInfo()
            print("--------------------metadata OK--------------------------------")

            # Subject
            sub = metaDataObj.subjectInfo()
            print("--------------------subjectInfo OK--------------------------------")
            # Project
            proj = metaDataObj.projectInfo()
            print("--------------------proj OK--------------------------------")

            # TSP
            tspObj = tsp.TSP(self.workingDirectory)
            tsparams = tspObj.export()
            print("--------------------TSP OK--------------------------------")

            # Measurements
            measObj = measurements.Measurements(self.workingDirectory)
            mea = measObj.measurementInfo(self.extra_settings)

            print("--------------------Measurements OK--------------------------------")

            # Create json
            root = {
                "results": ts + gvs + gps + emgExp + tsparams,
                "events": ev,
                "metadata": md,
                "measurements": mea,
                "clientId": self.clientId,
                "subject": sub,
                "project": proj,
            }

            return root
        else:
            root = {}
            return root


class WebReportUploader:
    def __init__(self, workingDirectory, configData):
        self.workingDirectory = workingDirectory
        self.configData = configData

    def upload(self, reportData):
        pathToLookForMp4 = get_parent_folder_absolute_path(self.workingDirectory)

        # check that clientId, baseUrl and token are specified in config.json
        if "clientId" in self.configData.keys():
            clientIdExists = True
        else:
            clientIdExists = False
            print("Error: Specify clientID in config.json")

        if "baseUrl" in self.configData.keys():
            baseUrlExists = True
        else:
            baseUrlExists = False
            print("Error: Specify baseUrl in config.json")

        if "token" in self.configData.keys():
            tokenExists = True
        else:
            tokenExists = False
            print("Error: Specify token in config.json")

        # Upload

        if clientIdExists and baseUrlExists and tokenExists:
            if reportData:
                baseUrl = self.configData["baseUrl"]

                headers = {"Authorization": "Bearer " + self.configData["token"]}

                reportReq = requests.post(baseUrl + "/api/v2/report/", json=reportData, headers=headers)
                if reportReq.status_code != 200:
                    print(reportReq.status_code)
                    print(reportReq.text)
                    raise Exception(
                        "Posting report data returned with a status code != 200, status code {code},\n response text {text}".format(
                            code=reportReq.status_code, text=reportReq.text
                        )
                    )
                reportResJson = reportReq.json()
                newReportId = reportResJson["id"]

                resourceOutput = get_mp4_filepaths(pathToLookForMp4)

                for index, resource in enumerate(resourceOutput):
                    fileData = {"file_%i" % index: open(resource, "rb")}
                    resourceReq = requests.post(
                        baseUrl + "/api/v2/report/" + newReportId + "/resource", files=fileData, headers=headers
                    )
                print("Report [%s] generated" % (str(newReportId)))
                webbrowser.open_new_tab(baseUrl + "/claim/" + newReportId)
            else:
                print("Error: No c3d file found that has been processed with Plugin-Gait.")
