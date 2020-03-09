# -*- coding: utf-8 -*-
import pyCGM2
from pyCGM2 import log
from pyCGM2.Utils.utils import *
from qtmWebGaitReport.pyCGM_workflows.reporting import create_web_report
from qtmWebGaitReport.pyCGM_workflows.reporting import create_pdf_report
from qtmWebGaitReport.pyCGM_workflows.reporting import load_settings_from_php
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

log.setLoggingLevel(logging.INFO)

warnings.simplefilter(action='ignore', category=FutureWarning)


def process_with_pycgm(session_xml, processed_folder):

    CGM2_Model = session_xml.Subsession.CGM2_Model.text
    logging.info("PROCESSING TYPE " + CGM2_Model)
    if CGM2_Model == "CGM1.0":
        # model = run_CGM1_workflow_and_return_model(
        #     session_xml, processed_folder)
        model = CGM1_workflow.main()
    elif CGM2_Model == "CGM1.1":
        model = CGM11_workflow.main()
    elif CGM2_Model == "CGM2.1-HJC":
        model = CGM21_workflow.main()
    elif CGM2_Model == "CGM2.2-IK":
        model = CGM22_workflow.main()
    elif CGM2_Model == "CGM2.3-skinClusters":
        # model = run_CGM23_workflow_and_return_model(
        #     session_xml, processed_folder)
        model = CGM23_workflow.main()
    elif CGM2_Model == "CGM2.4-ForeFoot":
        model = CGM24_workflow.main()
    else:
        raise Exception(
            "The pyCMG processing type is not implemented, you selected %s" % CGM2_Model)
    return model


def load_settings_php_if_possible(path_to_settings_file):
    if os.path.isfile(path_to_settings_file):
        settings_from_php = load_settings_from_php(path_to_settings_file)
    else:
        settings_from_php = {}
    return settings_from_php


def main(args):

    EventDetector_Zeni_main()
    dataQuality_main()

    work_folder = os.getcwd()
    settings_from_php = load_settings_php_if_possible(args.settings_php_path)
    session_xml_path = os.path.join(work_folder, "session.xml")
    session_xml = utils.read_session_xml(session_xml_path)
    processed_folder = os.path.join(work_folder, "processed")

    model = process_with_pycgm(session_xml, processed_folder)

    # --------------------------Reporting -----------------------
    webReportFlag = toBool(str(session_xml.find("Create_WEB_report").text))
    pdfReportFlag = toBool(str(session_xml.find("Create_PDF_report").text))

    if webReportFlag:
        create_web_report(session_xml, processed_folder, settings_from_php)
    if pdfReportFlag:
        create_pdf_report(session_xml, processed_folder, model)
