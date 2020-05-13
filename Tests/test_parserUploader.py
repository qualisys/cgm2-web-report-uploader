from qtmWebGaitReport.parserUploader import ReportJsonGenerator
from qtmWebGaitReport.qtmFilters import loadConfigData
from qtmWebGaitReport.CGM_workflow_main import __create_subject_metadata
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

    subjectInfo = __create_subject_metadata(sessionXML, session_type)
    # initiate parser uploader
    processedDir = os.path.join(testDataPath, "processed")
    reportJsonGenerator = ReportJsonGenerator(processedDir,
                                              configData["clientId"], modelledTrials,
                                              subjectInfo, sessionDate)
    return reportJsonGenerator


resave_all_test_data = False


def update_test_data(savedDataFilePath, generatedReportJson):
    with open(savedDataFilePath, 'w') as outfile:
        # for saving updated generated json
        json.dump(generatedReportJson, outfile, indent=4)


def check_key_value_pairs(generated_json, loaded_json):
    for key, val in generated_json.items():
        assert key in loaded_json.keys(
        ), "{} not in loaded reoport json but exists in generated one".format(key)
        assert val == loaded_json[key], "value for entry under key = {} differs from loaded vs generated".format(
            key)


def get_generated_and_loaded_json(folder_name):
    testDataPath, savedDataFilePath = get_paths(folder_name)
    parser = prepare_parser(testDataPath)
    generatedReportJson = parser.createReportJson()

    if resave_all_test_data:
        update_test_data(savedDataFilePath, generatedReportJson)
    loadedReportJson = loadJson(savedDataFilePath)

    return generatedReportJson, loadedReportJson


class TestGenerateReportJson():
    def test_clinical_gait_example(self):
        generatedReportJson, loadedReportJson = get_generated_and_loaded_json(
            "ClinicalGaitExample")

        check_key_value_pairs(generatedReportJson, loadedReportJson)

    def test_example_with_force_data(self):
        generatedReportJson, loadedReportJson = get_generated_and_loaded_json(
            "WithForceData")

        check_key_value_pairs(generatedReportJson, loadedReportJson)
    
    def test_example_with_new_paf_fields(self):
        generatedReportJson, loadedReportJson = get_generated_and_loaded_json(
            "WithNewPafFields")

        check_key_value_pairs(generatedReportJson, loadedReportJson)
