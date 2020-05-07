# -*- coding: utf-8 -*-
import pyCGM2
from pyCGM2 import log
from pyCGM2.Utils.utils import *
from qtmWebGaitReport.pyCGM_workflows.reporting import create_web_report
from qtmWebGaitReport.pyCGM_workflows.reporting import create_pdf_report
from qtmWebGaitReport.pyCGM_workflows.reporting import load_settings_from_php
from qtmWebGaitReport.pyCGM_workflows.reporting import load_user_settings_yaml
from qtmWebGaitReport.pyCGM_workflows import CGM1_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM11_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM21_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM22_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM23_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM24_workflow
from qtmWebGaitReport.EventDetector_Zeni import main as EventDetector_Zeni_main
from qtmWebGaitReport.pyCGM2_dataQuality import main as dataQuality_main
from qtmWebGaitReport import utils
import logging
import warnings
import os

from pathlib2 import Path

log.setLoggingLevel(logging.INFO)

warnings.simplefilter(action='ignore', category=FutureWarning)


def process_and_return_model(model_type):
    if model_type == "CGM1.0":
        model = CGM1_workflow.main()
    elif model_type == "CGM1.1":
        model = CGM11_workflow.main()
    elif model_type == "CGM2.1-HJC":
        model = CGM21_workflow.main()
    elif model_type == "CGM2.2-IK":
        model = CGM22_workflow.main()
    elif model_type == "CGM2.3-skinClusters":
        model = CGM23_workflow.main()
    elif model_type == "CGM2.4-ForeFoot":
        model = CGM24_workflow.main()
    else:
        raise Exception(
            "The pyCMG processing type is not implemented, you selected %s" % model_type)
    return model


def process_with_pycgm(session_xml, processed_folder):

    CGM2_Model = session_xml.Subsession.CGM2_Model.text
    logging.info("PROCESSING TYPE " + CGM2_Model)
    model = process_and_return_model(CGM2_Model)
    return model


def load_settings_php_if_possible(path_to_settings_file):
    if os.path.isfile(path_to_settings_file):
        settings_from_php = load_settings_from_php(path_to_settings_file)
    else:
        settings_from_php = {}
    return settings_from_php


def load_user_settings_if_possible(path_to_file):
    if os.path.isfile(path_to_file):
        settings = load_user_settings_yaml(path_to_file)
    else:
        settings = {}
    return settings


def load_extra_settings(path_to_templates):
    settings = load_settings_php_if_possible(
        os.path.join(path_to_templates, "settings.php"))
    user_settings = load_user_settings_if_possible(os.path.join(
        path_to_templates, os.pardir, "Settings", "User Settings.paf"))
    settings.update(user_settings)
    return settings

def delete_c3d_files_in(folder_path):
    folder_path = Path(folder_path)
    for c3d_file_path in folder_path.glob("*.c3d"):
        c3d_file_path.unlink()

def main(args):
    work_folder = os.getcwd()

    settings = load_extra_settings(args.templates_path)
    session_xml_path = os.path.join(work_folder, "session.xml")
    session_xml = utils.read_session_xml(session_xml_path)
    processed_folder = os.path.join(work_folder, "processed")

    delete_c3d_files_in(processed_folder)

    EventDetector_Zeni_main()
    dataQuality_main()

    model = process_with_pycgm(session_xml, processed_folder)

    # --------------------------Reporting -----------------------
    webReportFlag = args.web_report
    pdfReportFlag = args.pdf_report

    if webReportFlag:
        create_web_report(session_xml, processed_folder, settings)
    if pdfReportFlag:
        create_pdf_report(session_xml, processed_folder, model)
