import sys
import os
import json
import qtmWebGaitReport
from qtmWebGaitReport import parserUploader


class WebReportFilter(object):
    def __init__(self,workingDirectory,modelledC3dfilenames,subjectInfo,sessionDate):

        if os.path.isfile(qtmWebGaitReport.GAIT_WEB_REPORT_PATH + 'config.json'):
            with open(qtmWebGaitReport.GAIT_WEB_REPORT_PATH + 'config.json') as jsonDataFile:
                configData = json.load(jsonDataFile)
        else:
            print "Config.json not found at " + os.getcwd()


        self.processing = parserUploader.ParserUploader(workingDirectory,
                    configData,modelledC3dfilenames,
                    subjectInfo,sessionDate)


    def exportJson(self):

        jsonData = self.processing.createReportJson()

        with open(str(""+"jsonData.json"), 'w') as outfile:
            json.dump(jsonData, outfile,indent=4)


    def upload(self):
        self.processing.Upload()
