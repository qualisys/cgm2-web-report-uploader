import sys
import os
import json
import qtmWebGaitReport
from qtmWebGaitReport.parserUploader import ReportJsonGenerator
from qtmWebGaitReport.parserUploader import WebReportUploader


def loadConfigData(directoryPath=None):
    configData = {}
    configPathsToCheck = [
        os.path.join(directoryPath, "upload-token.json"),
        os.path.join(os.path.abspath(os.path.join(directoryPath, os.pardir)),
                     "upload-token.json"),
        os.path.join(qtmWebGaitReport.PATH_TO_MAIN, 'config.json')
    ]
    for configPath in configPathsToCheck:
        print("Checking path: " + configPath)
        if os.path.isfile(configPath):
            with open(configPath) as jsonDataFile:
                configData = json.load(jsonDataFile)
            print("Config loaded from " + configPath)
            break
    if configData == {}:
        raise Exception("Config file not found, file paths investigated: [\n{}\n]".format(
            "\n".join(configPathsToCheck)))
    return configData


class WebReportFilter(object):
<<<<<<< HEAD
    def __init__(self,workingDirectory,modelledC3dfilenames,subjectInfo,sessionDate):

        if os.path.isfile(qtmWebGaitReport.GAIT_WEB_REPORT_PATH + 'config.json'):
            with open(qtmWebGaitReport.GAIT_WEB_REPORT_PATH + 'config.json') as jsonDataFile:
                configData = json.load(jsonDataFile)
        else:
            raise Exception ("Config.json not found at " + qtmWebGaitReport.GAIT_WEB_REPORT_PATH)

=======
    def __init__(self, workingDirectory, modelledC3dfilenames, subjectInfo, sessionDate, settings_from_php={}):
        configData = loadConfigData(workingDirectory)
>>>>>>> b66937417b75b431de7dad13b558ca741ef68fbe

        self.reportGenerator = ReportJsonGenerator(
            workingDirectory, configData["clientId"], modelledC3dfilenames, subjectInfo, sessionDate, settings_from_php)
        self.reportData = self.reportGenerator.createReportJson()

        self.uploader = WebReportUploader(workingDirectory, configData)

    def exportJson(self):
        with open("session_data.json", 'w') as outfile:
            json.dump(self.reportData, outfile, indent=4)

    def getReportData(self):
        return self.reportData

    def upload(self):
        self.uploader.upload(self.reportData)
