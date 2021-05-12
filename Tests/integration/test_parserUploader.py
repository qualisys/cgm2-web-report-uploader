import json
import os

import pytest
from pyCGM2.qtm import qtmTools
from qtmWebGaitReport import utils
from qtmWebGaitReport.parserUploader import ReportJsonGenerator
from qtmWebGaitReport.qtmFilters import loadConfigData
from qtmWebGaitReport.session_xml import create_subject_metadata, load_session_xml_soup


def saveExampleOutputToJson(dataDict, filePath="jsonData.json"):
    with open(filePath, "w") as outfile:
        json.dump(dataDict, outfile)


def loadJson(filePath):
    with open(filePath, "r") as f:
        dataDict = json.load(f)
    return dataDict


configData = loadConfigData(os.path.join(os.getcwd(), "TestFiles"))


def get_paths(example_folder_name):
    testDataPath = os.path.join(os.getcwd(), "TestFiles", example_folder_name)
    savedDataFilePath = os.path.join(testDataPath, "savedJsonData.json")
    return testDataPath, savedDataFilePath


def prepare_parser(testDataPath):
    # this code is mostly duplicate from the PAF modules template, possibly rework where the functionality goes
    session_xml_path = os.path.join(testDataPath, "session.xml")
    sessionXML = load_session_xml_soup(session_xml_path)
    sessionDate = utils.get_creation_date(sessionXML)
    session_type = qtmTools.detectMeasurementType(sessionXML)[0]  # in this example there is only one

    modelledTrials = []
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)
    for dynamicMeasurement in dynamicMeasurements:
        if qtmTools.isType(dynamicMeasurement, session_type):
            filename = qtmTools.getFilename(dynamicMeasurement)
            modelledTrials.append(filename)

    subjectInfo = create_subject_metadata(sessionXML)
    # initiate parser uploader
    processedDir = os.path.join(testDataPath, "processed")
    reportJsonGenerator = ReportJsonGenerator(
        processedDir, configData["clientId"], modelledTrials, subjectInfo, sessionDate
    )
    return reportJsonGenerator


resave_all_test_data = False


def update_test_data(savedDataFilePath, generatedReportJson):
    with open(savedDataFilePath, "w") as outfile:
        # for saving updated generated json
        json.dump(generatedReportJson, outfile, indent=4)


def check_key_value_pairs(generated_json, loaded_json):
    for key, val in generated_json.items():
        assert key in loaded_json.keys(), f"{key} not in loaded report json but exists in generated one"
        if key == "results":
            for loaded_result in loaded_json[key]:
                loaded_id = loaded_result["id"]
                gen_result = [x for x in loaded_json[key] if x["id"] == loaded_id]
                assert (
                    len(gen_result) == 1
                ), f"Expected exactly one result in generated result with id {loaded_id}, but got {gen_result}"
                assert gen_result[0] == loaded_result
        elif key == "measurements":
            # DOES NOT COMPARE creation date and time
            assert len(loaded_json[key]) == len(
                generated_json[key]
            ), "Loaded and generated measurements entries have differing lenths"
            for loaded, generated in zip(loaded_json[key], generated_json[key]):
                loaded["fields"] = [x for x in loaded["fields"] if x["id"] not in ["Creation date", "Creation time"]]
                generated["fields"] = [
                    x for x in generated["fields"] if x["id"] not in ["Creation date", "Creation time"]
                ]
                assert loaded == generated

        else:
            assert val == loaded_json[key], f"value for entry under key = {key} differs from loaded vs generated"


def get_generated_and_loaded_json(folder_name):
    testDataPath, savedDataFilePath = get_paths(folder_name)
    parser = prepare_parser(testDataPath)
    generatedReportJson = parser.createReportJson()

    if resave_all_test_data:
        update_test_data(savedDataFilePath, generatedReportJson)
    loadedReportJson = loadJson(savedDataFilePath)

    return generatedReportJson, loadedReportJson


class TestGenerateReportJson:
    def test_clinical_gait_example(self):
        generatedReportJson, loadedReportJson = get_generated_and_loaded_json("ClinicalGaitExample")

        check_key_value_pairs(generatedReportJson, loadedReportJson)

    def test_example_with_force_data(self):
        generatedReportJson, loadedReportJson = get_generated_and_loaded_json("WithForceData")

        check_key_value_pairs(generatedReportJson, loadedReportJson)

    def test_example_with_new_paf_fields(self):
        generatedReportJson, loadedReportJson = get_generated_and_loaded_json("WithNewPafFields")

        check_key_value_pairs(generatedReportJson, loadedReportJson)

