from qtmWebGaitReport import parserUploader
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


testDataPath = os.path.join(os.getcwd(), "TestFiles", "ClinicalGaitExample")
savedDataFilePath = os.path.join(testDataPath, "savedJsonData.json")
processedDir = os.path.join(testDataPath, "processed")
configData = loadConfigData(os.path.join(os.getcwd(),
                                         "TestFiles", 'example_config.json'))


def prepare_parser():
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
    parser = parserUploader.ParserUploader(processedDir,
                                           configData, modelledTrials,
                                           subjectInfo, sessionDate)
    return parser


class TestClinicalGateExample():
    def testCreateReportJson(self):
        parser = prepare_parser()
        generatedReportJson = parser.createReportJson()
        loadedReportJson = loadJson(savedDataFilePath)

        assert generatedReportJson == loadedReportJson, "generated report json differs from loaded one"
