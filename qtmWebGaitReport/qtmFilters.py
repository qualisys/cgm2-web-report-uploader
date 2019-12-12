import sys
import os
import json
import qtmWebGaitReport
from qtmWebGaitReport import parserUploader


def loadConfigData(configPath):
    if os.path.isfile(configPath):
        with open(configPath) as jsonDataFile:
            configData = json.load(jsonDataFile)
    else:
        raise Exception("Config file not found, file path investigated: " +
                        configPath)
    return configData


class WebReportFilter(object):
    def __init__(self, workingDirectory, modelledC3dfilenames, subjectInfo, sessionDate):
        configData = loadConfigData(os.path.join(
            qtmWebGaitReport.GAIT_WEB_REPORT_PATH, 'config.json'))

        self.processing = parserUploader.ParserUploader(workingDirectory,
                                                        configData, modelledC3dfilenames,
                                                        subjectInfo, sessionDate)

    def exportJson(self):

        jsonData = self.processing.createReportJson()

        with open("jsonData.json", 'w') as outfile:
            json.dump(jsonData, outfile, indent=4)

    def upload(self):
        self.processing.Upload()
