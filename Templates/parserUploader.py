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

workingDirectory = "E:\\Qualisys_repository\\Gait-Web-Importer\\Data\\myMess\\"
#templatesDirectory = os.getcwd()

class ParserUploader:
    def __init__(self,workingDirectory):
        self.workingDirectory = workingDirectory
        
        #load config.json
        if path.isfile(getcwd() + '/config.json'):
            with open(getcwd() + '/config.json') as jsonDataFile:
                self.configData = json.load(jsonDataFile)
        else:
            print "Config.json not found at " + getcwd()

    def createReportJson(self):
        c3dValObj = c3dValidation.c3dValidation(self.workingDirectory)
        measurementNames = c3dValObj.getValidC3dList(True)
        fileNames = c3dValObj.getValidC3dList(False)
        eventsDict = dict()
        null = None

        if fileNames: #empty list means c3d does not contain Plugin-Gait created 'LAnkleAngles' or there are no events
            for filename in fileNames:
                acq = qtools.fileOpen(filename)
                
                frameRate = acq.GetPointFrequency()
                analogRate = acq.GetAnalogFrequency()
            
            #Timeseries
            tsObj = timeseries.Timeseries(self.workingDirectory)
            tseries = tsObj.calculateTimeseries()
            sigList = qtools.getKeyNameList(tseries)
            
            ts = list()
            for sig in sigList:
                ts.append(qtools.getSeriesExport(tseries, measurementNames, sig, "series", 4, frameRate, "LINK_MODEL_BASED/ORIGINAL"))
    
            #GVS
            mapProfile = map2.MAP(self.workingDirectory)
            gvsScore = mapProfile.calculateGVS()[1]
            sigList = qtools.getKeyNameList(gvsScore)
            
            gvs = list()    
            for sig in sigList:
                gvs.append(qtools.getSeriesExport(gvsScore, measurementNames, sig, "scalar", 4, null, "LINK_MODEL_BASED/ORIGINAL"))
            
            #GPS
            gpsScoreLeft = mapProfile.calculateGPS()[0]
            gpsScoreRight = mapProfile.calculateGPS()[1]
            gpsScoreOverall = mapProfile.calculateGPS()[2]
            
            gpsLeft = mapProfile.gpsExport(gpsScoreLeft,"Left_GPS_ln_mean",frameRate)
            gpsRight = mapProfile.gpsExport(gpsScoreRight,"Right_GPS_ln_mean",frameRate)
            gpsOverall = mapProfile.gpsExport(gpsScoreOverall,"Overall_GPS_ln_mean",frameRate)
            gps = gpsLeft + gpsRight + gpsOverall
            
            #EMG
            emgObj = emg.EMG(self.workingDirectory)
            emgData = emgObj.calculateRawEMG()
            sigList = qtools.getKeyNameList(emgData)
            
            emgExp = list()
            for sig in sigList:
                emgExp.append(qtools.getSeriesExport(emgData,measurementNames,sig, "series", 8, analogRate, "ANALOG/EMG_RAW_web"))
    
            #Events
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
                        "data": qtools.setEventData(eventData,measurementNames,label)
                        }
            
            ev = qtools.loadEvents(maxEventList ,eventsDict)
            
            #MetaData
            metaDataObj = metadata.Metadata(self.workingDirectory)
            md = metaDataObj.medatadaInfo()
            
            #Subject
            sub = metaDataObj.subjectInfo()
            
            #Project
            proj = metaDataObj.projectInfo()
            
            #TSP
            tspObj = tsp.TSP(self.workingDirectory)
            tsparams = tspObj.export()
            
            #Measurements
            measObj = measurements.Measurements(self.workingDirectory)
            mea = measObj.measurementInfo()
            
            #Create json
            root = {
                    "results": ts + gvs + gps + emgExp + tsparams,
                    "events": ev,
                    "metadata": md,
                    "measurements": mea,
                    "clientId": self.configData["clientId"],
                	"subject": sub,
                	"project": proj
                    }
            
            #Write to json file
    #       import json
    #         with open(self.workingDirectory + 'reportData.json', 'w') as f:
    #            json.dump(root, f, indent=4,sort_keys=True)
            return root
        else:
            root = []
            return root
          
    def Upload(self):
        #Convert Avi to mp4
        videoObj = avi2mp4.AviToMp4(self.workingDirectory)
        videoObj.convertAviToMp4()

        #check that clientId, baseUrl and token are specified in config.json
        if self.configData["clientId"]:
            clientIdExists = True
        else:
            clientIdExists = False
            print "Error: Specify clientID in config.json"
            
        if self.configData["baseUrl"]:
            baseUrlExists = True
        else:
            baseUrlExists = False
            print "Error: Specify baseUrl in config.json"
            
        if self.configData["token"]:
            tokenExists = True
        else:
            tokenExists = False
            print "Error: Specify token in config.json"
            
        #Upload
        reportData = self.createReportJson()
        
        if clientIdExists and baseUrlExists and tokenExists:
            if reportData:
                baseUrl = self.configData["baseUrl"]
                
                # Get upload token
                uploadToken = self.configData["token"]
                headers = {'Authorization': 'Bearer ' + uploadToken}
                reportReq = requests.post(baseUrl + '/api/v2/report/', json=reportData, headers=headers)
                reportResJson = reportReq.json()
                newReportId = reportResJson['id']
                resourceOutput = videoObj.getMp4Filenames(False)
                
                for index, resource in enumerate(resourceOutput):
                    fileData = { 'file_' + `index`: open(resource,'rb') }
                    resourceReq = requests.post(baseUrl + '/api/v2/report/' + newReportId + '/resource', files=fileData, headers=headers)
            else:
                print "Error: No c3d file found that has been processed with Plugin-Gait."

if __name__ == "__main__":
    a = ParserUploader(workingDirectory)
    #b = a.Upload()
    c = a.createReportJson()