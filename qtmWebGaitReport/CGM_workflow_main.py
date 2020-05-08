# -*- coding: utf-8 -*-
import logging
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import os
import yaml

from qtmWebGaitReport import qtmFilters
from qtmWebGaitReport.convert_report_json_to_regression_test_xml import save_session_data_xml_from
from pathlib2 import Path


from pyCGM2.Apps.QtmApps.CGMi import CGM1_workflow
from pyCGM2.Apps.QtmApps.CGMi import CGM11_workflow
from pyCGM2.Apps.QtmApps.CGMi import CGM21_workflow
from pyCGM2.Apps.QtmApps.CGMi import CGM22_workflow
from pyCGM2.Apps.QtmApps.CGMi import CGM23_workflow
from pyCGM2.Apps.QtmApps.CGMi import CGM24_workflow
from pyCGM2.qtm import qtmTools

from pyCGM2.Utils import files

SESSION_XML_FILENAME = "session.xml"

# ---- settings-----
def __load_settings_from_php(file_path):
    settings_to_find = ["$force_threshold"]
    with open(file_path, "r") as f:
        all_lines = f.readlines()
        settings_dict = {
            x.split(" ")[0].replace("$", ""): int(x.split("= ")[-1].split(";")[0]) for x in all_lines
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
    settings = __load_settings_php_if_possible(
        os.path.join(path_to_templates, "settings.php"))
    user_settings = __load_user_settings_if_possible(os.path.join(
        path_to_templates, os.pardir, "Settings", "User Settings.paf"))
    settings.update(user_settings)
    return settings

def delete_c3d_files_in(folder_path):
    folder_path = Path(folder_path)
    for c3d_file_path in folder_path.glob("*.c3d"):
        c3d_file_path.unlink()

# ---- process with pyCGM2-----
def process_and_return_model(model_type,generate_pdf_report=False):
    if model_type == "CGM1.0":
        model = CGM1_workflow.main(SESSION_XML_FILENAME,generate_pdf_report)
    elif model_type == "CGM1.1":
        model = CGM11_workflow.main(SESSION_XML_FILENAME,generate_pdf_report)
    elif model_type == "CGM2.1-HJC":
        model = CGM21_workflow.main(SESSION_XML_FILENAME,generate_pdf_report)
    elif model_type == "CGM2.2-IK":
        model = CGM22_workflow.main(SESSION_XML_FILENAME,generate_pdf_report)
    elif model_type == "CGM2.3-skinClusters":
        model = CGM23_workflow.main(SESSION_XML_FILENAME,generate_pdf_report)
    elif model_type == "CGM2.4-ForeFoot":
        model = CGM24_workflow.main(SESSION_XML_FILENAME,generate_pdf_report)
    else:
        raise Exception(
            "The pyCMG processing type is not implemented, you selected %s" % model_type)
    return model


def process_with_pycgm(work_folder,generate_pdf_report):
    session_xml = files.readXml(work_folder+"\\", SESSION_XML_FILENAME)
    CGM2_Model = session_xml.Subsession.CGM2_Model.text
    logging.info("PROCESSING TYPE " + CGM2_Model)
    model = process_and_return_model(CGM2_Model,generate_pdf_report)
    return model



#----web report---------

def __create_subject_metadata(session_xml, measurement_type):
    return {
        "patientName": session_xml.find("First_name").text + " " + session_xml.find("Last_name").text,
        "patientID": session_xml.find("Patient_ID").text,
        "bodyHeight": session_xml.find("Height").text,
        "bodyWeight": session_xml.find("Weight").text,
        "diagnosis": session_xml.find("Diagnosis").text,
        "dob": session_xml.find("Date_of_birth").text,
        "sex": session_xml.find("Sex").text,
        "test condition": measurement_type,
        "subSessionType": session_xml.find("Subsession").get("Type"),
        "gmfcs": session_xml.find("Gross_Motor_Function_Classification").text,
        "fms": session_xml.find("Functional_Mobility_Scale").text}
  


def create_web_report(session_xml, data_path, settings_from_php):

    measurement_types = qtmTools.detectMeasurementType(session_xml)
    for measurement_type in measurement_types:

        modelledTrials = qtmTools.get_modelled_trials(session_xml, measurement_type)
        subjectMd = __create_subject_metadata(session_xml, measurement_type)
        sessionDate = qtmTools.get_creation_date(session_xml)

        report = qtmFilters.WebReportFilter(
            data_path, modelledTrials, subjectMd, sessionDate, settings_from_php)
        # report.exportJson()
        save_session_data_xml_from(report.getReportData())
        report.upload()
        logging.info("qualisys Web Report exported")



def main(args):
    work_folder = os.getcwd()
    
      
    processed_folder = os.path.join(work_folder, "processed")
    delete_c3d_files_in(processed_folder)

    # run and process pyCGM2
    model = process_with_pycgm(work_folder,args.pdf_report) # i keep  the model as output , just in case of futher use

    webReportFlag = args.web_report
    if webReportFlag:
        
        settings = load_extra_settings(args.templates_path)
        session_xml = files.readXml(work_folder+"\\", SESSION_XML_FILENAME)
        create_web_report(session_xml, processed_folder, settings)
