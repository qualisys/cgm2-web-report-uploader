from qtmWebGaitReport.parserUploader import ReportJsonGenerator
from qtmWebGaitReport.qtmFilters import loadConfigData
from qtmWebGaitReport.CGM_workflow_main import create_subject_metadata
from pyCGM2.qtm import qtmTools
from qtmWebGaitReport import utils

import json
import pytest
import os


def saveExampleOutputToJson(dataDict, filePath="jsonData.json"):
    with open(filePath, 'w') as outfile:
        json.dump(dataDict, outfile)


def loadJson(filePath):
    with open(filePath, "r") as f:
        dataDict = json.load(f)
    return dataDict


configData = loadConfigData(os.path.join(os.getcwd(),
                                         "TestFiles"))


def get_paths(example_folder_name):
    testDataPath = os.path.join(
        os.getcwd(), "TestFiles", example_folder_name)
    savedDataFilePath = os.path.join(testDataPath, "savedJsonData.json")
    return testDataPath, savedDataFilePath


def prepare_parser(testDataPath):
    # this code is mostly duplicate from the PAF modules template, possibly rework where the functionality goes
    session_xml_path = os.path.join(testDataPath, "session.xml")
    sessionXML = utils.read_session_xml(session_xml_path)
    sessionDate = utils.get_creation_date(sessionXML)
    session_type = qtmTools.detectMeasurementType(
        sessionXML)[0]  # in this example there is only one

    modelledTrials = []
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)
    for dynamicMeasurement in dynamicMeasurements:
        if qtmTools.isType(dynamicMeasurement, session_type):
            filename = qtmTools.getFilename(dynamicMeasurement)
            modelledTrials.append(filename)

    subjectInfo = create_subject_metadata(sessionXML, session_type)
    # initiate parser uploader
    processedDir = os.path.join(testDataPath, "processed")
    reportJsonGenerator = ReportJsonGenerator(processedDir,
                                              configData["clientId"], modelledTrials,
                                              subjectInfo, sessionDate)
    return reportJsonGenerator

# with open(savedDataFilePath, 'w') as outfile: json.dump(generatedReportJson, outfile, indent=4) # for saving updated generated json


class TestClinicalGateExample():
    def testCreateReportJson(self):
        testDataPath, savedDataFilePath = get_paths("ClinicalGaitExample")
        parser = prepare_parser(testDataPath)
        generatedReportJson = parser.createReportJson()
        loadedReportJson = loadJson(savedDataFilePath)

        for key, val in generatedReportJson.items():
            assert key in loadedReportJson.keys(
            ), "{} not in loaded reoport json but exists in generated one".format(key)
            assert val == loadedReportJson[key], "value for entry under key = {} differs from loaded vs generated".format(
                key)
