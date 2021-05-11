# -*- coding: utf-8 -*-
import logging
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)
import os
from pathlib import Path

import yaml
from pyCGM2.Apps.QtmApps.CGMi import (
    CGM1_workflow,
    CGM11_workflow,
    CGM21_workflow,
    CGM22_workflow,
    CGM23_workflow,
    CGM24_workflow,
    CGM25_workflow,
    CGM26_workflow,
)
from pyCGM2.qtm import qtmTools
from pyCGM2.Utils import files

from qtmWebGaitReport import qtmFilters
from qtmWebGaitReport.convert_report_json_to_regression_test_xml import save_session_data_xml_from

SESSION_XML_FILENAME = "session.xml"

# ---- settings-----
def __load_settings_from_php(file_path):
    settings_to_find = ["$force_threshold"]
    with open(file_path, "r") as f:
        all_lines = f.readlines()
        settings_dict = {
            x.split(" ")[0].replace("$", ""): int(x.split("= ")[-1].split(";")[0])
            for x in all_lines
            if x.split(" ")[0] in settings_to_find
        }
    return settings_dict


def __load_user_settings_yaml(path):
    with open(path, "r") as f:
        settings = yaml.load(f)
    return settings


def __load_settings_php_if_possible(path_to_settings_file):
    if os.path.isfile(path_to_settings_file):
        settings_from_php = __load_settings_from_php(path_to_settings_file)
    else:
        settings_from_php = {}
    return settings_from_php


def __load_user_settings_if_possible(path_to_file):
    if os.path.isfile(path_to_file):
        settings = __load_user_settings_yaml(path_to_file)
    else:
        settings = {}
    return settings


def load_extra_settings(path_to_templates):
    settings = __load_settings_php_if_possible(os.path.join(path_to_templates, "settings.php"))
    user_settings = __load_user_settings_if_possible(
        os.path.join(path_to_templates, os.pardir, "Settings", "User Settings.paf")
    )
    settings.update(user_settings)
    return settings


def delete_c3d_files_in(folder_path):
    folder_path = Path(folder_path)
    for c3d_file_path in folder_path.glob("*.c3d"):
        c3d_file_path.unlink()


_cgm2_processing_functions = {
    "CGM1.0": CGM1_workflow.main,
    "CGM1.1": CGM11_workflow.main,
    "CGM2.1-HJC": CGM21_workflow.main,
    "CGM2.2-IK": CGM22_workflow.main,
    "CGM2.3-skinClusters": CGM23_workflow.main,
    "CGM2.4-ForeFoot": CGM24_workflow.main,
    "CGM2.5-UpperLimb": CGM25_workflow.main,
    "CGM2.6-FunctionalKnee": CGM26_workflow.main,
}
# ---- process with pyCGM2-----
def process_and_return_model(model_type, generate_pdf_report=False, check_events_in_mokka=True):
    if model_type in _cgm2_processing_functions.keys():
        process = _cgm2_processing_functions[model_type]
        model = process(SESSION_XML_FILENAME, generate_pdf_report, check_events_in_mokka)
    else:
        raise Exception("The pyCMG processing type is not implemented, you selected %s" % model_type)
    return model


def process_with_pycgm(work_folder, generate_pdf_report, check_events_in_mokka=True):
    session_xml = files.readXml(work_folder + "\\", SESSION_XML_FILENAME)
    CGM2_Model = session_xml.Subsession.CGM2_Model.text
    logging.info("PROCESSING TYPE " + CGM2_Model)
    model = process_and_return_model(CGM2_Model, generate_pdf_report, check_events_in_mokka=check_events_in_mokka)
    return model


# ----web report---------


def __create_subject_metadata(session_xml):
    result = {
        "Display name": session_xml.find("First_name").text + " " + session_xml.find("Last_name").text,
        "First name": session_xml.find("First_name").text,
        "Last name": session_xml.find("Last_name").text,
        "Patient ID": session_xml.find("Patient_ID").text,
        "Height": session_xml.find("Height").text,
        "Weight": session_xml.find("Weight").text,
        "Diagnosis": session_xml.find("Diagnosis").text,
        "Date of birth": session_xml.find("Date_of_birth").text,
        "Sex": session_xml.find("Sex").text,
        "Test condition": session_xml.find("Test_condition").text,
        "Sub Session Type": session_xml.find("Subsession").get("Type"),
        "Gross Motor Function Classification": session_xml.find("Gross_Motor_Function_Classification").text,
        "Functional Mobility Scale": session_xml.find("Functional_Mobility_Scale").text,
    }
    if session_xml.find("CGM2_Model") is not None:
        result["CGM2 Model"] = session_xml.find("CGM2_Model").text
    return result


def create_web_report(session_xml, data_path, settings_from_php):

    measurement_types = qtmTools.detectMeasurementType(session_xml)
    for measurement_type in measurement_types:

        modelledTrials = qtmTools.get_modelled_trials(session_xml, measurement_type)
        subjectMd = __create_subject_metadata(session_xml)
        sessionDate = qtmTools.get_creation_date(session_xml)

        report = qtmFilters.WebReportFilter(data_path, modelledTrials, subjectMd, sessionDate, settings_from_php)
        # report.exportJson()
        save_session_data_xml_from(report.getReportData())
        report.upload()
        logging.info("qualisys Web Report exported")


def main(args):
    work_folder = os.getcwd()

    processed_folder = os.path.join(work_folder, "processed")
    delete_c3d_files_in(processed_folder)

    # run and process pyCGM2
    check_events_in_mokka = True if args.skip_mokka == False else False
    model = process_with_pycgm(
        work_folder, args.pdf_report, check_events_in_mokka=check_events_in_mokka
    )  # i keep  the model as output , just in case of futher use

    webReportFlag = args.web_report
    if webReportFlag:

        settings = load_extra_settings(args.templates_path)
        session_xml = files.readXml(work_folder + "\\", SESSION_XML_FILENAME)
        create_web_report(session_xml, processed_folder, settings)
