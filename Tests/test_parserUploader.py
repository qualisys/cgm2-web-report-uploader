from qtmWebGaitReport.parserUploader import WebReportUploader
from qtmWebGaitReport.qtmFilters import loadConfigData
from pyCGM2.qtm import qtmTools
from pyCGM2.Utils import files

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
                                         "TestFiles", 'example_config.json'))


def get_paths(example_folder_name):
    testDataPath = os.path.join(
        os.getcwd(), "TestFiles", example_folder_name)
    savedDataFilePath = os.path.join(testDataPath, "savedJsonData.json")
    return testDataPath, savedDataFilePath


def prepare_parser(testDataPath):
    # this code is mostly duplicate from the PAF modules template, possibly rework where the functionality goes
    sessionXMLfilename = "session.xml"
    # the + "\\" is because of the Util file in pyCGM2 to update it I would need make a pull request to the pyCGM2 library
    sessionXML = files.readXml(testDataPath+"\\", sessionXMLfilename)
    sessionDate = files.getFileCreationDate(
        os.path.join(testDataPath, sessionXMLfilename))
    session_type = qtmTools.detectMeasurementType(
        sessionXML)[0]  # in this example there is only one

    modelledTrials = []
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)
    for dynamicMeasurement in dynamicMeasurements:
        if qtmTools.isType(dynamicMeasurement, session_type):
            filename = qtmTools.getFilename(dynamicMeasurement)
            modelledTrials.append(filename)

    subjectInfo = {"patientName": sessionXML.find("Last_name").text + " " + sessionXML.find("First_name").text,
                   "bodyHeight": sessionXML.find("Height").text,
                   "bodyWeight": sessionXML.find("Weight").text,
                   "diagnosis": sessionXML.find("Diagnosis").text,
                   "dob": sessionXML.find("Date_of_birth").text,
                   "sex": sessionXML.find("Sex").text,
                   "test condition": session_type,
                   "gmfcs": sessionXML.find("Gross_Motor_Function_Classification").text,
                   "fms": sessionXML.find("Functional_Mobility_Scale").text}
    # initiate parser uploader
    processedDir = os.path.join(testDataPath, "processed")
    parser = WebReportUploader(processedDir,
                               configData, modelledTrials,
                               subjectInfo, sessionDate)
    return parser


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
