# -*- coding: utf-8 -*-
import pyCGM2
from pyCGM2 import log
from pyCGM2.Report import normativeDatasets
from pyCGM2.Utils.utils import *
from qtmWebGaitReport.pyCGM_workflows.reporting import create_web_report
from qtmWebGaitReport.pyCGM_workflows.reporting import create_pdf_report
from qtmWebGaitReport.pyCGM_workflows import CGM1_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM11_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM21_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM22_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM23_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM24_workflow
from qtmWebGaitReport import utils
import logging
import warnings
import os

log.setLoggingLevel(logging.INFO)

warnings.simplefilter(action='ignore', category=FutureWarning)


def main():
    work_folder = os.getcwd()
    session_xml_path = os.path.join(work_folder, "session.xml")
    session_xml = utils.read_session_xml(session_xml_path)
    processed_folder = os.path.join(work_folder, "processed")
    pyCGM_processing_type = session_xml.Subsession.pyCGM_Processing_Type.text
    logging.info("PROCESSING TYPE " + pyCGM_processing_type)
    if pyCGM_processing_type == "pyCGM1":
        # model = run_CGM1_workflow_and_return_model(
        #     session_xml, processed_folder)
        model = CGM1_workflow.main()
    elif pyCGM_processing_type == "pyCGM11":
        model = CGM11_workflow.main()
    elif pyCGM_processing_type == "pyCGM21":
        model = CGM21_workflow.main()
    elif pyCGM_processing_type == "pyCGM22":
        model = CGM22_workflow.main()
    elif pyCGM_processing_type == "pyCGM23":
        # model = run_CGM23_workflow_and_return_model(
        #     session_xml, processed_folder)
        model = CGM23_workflow.main()
    elif pyCGM_processing_type == "pyCGM24":
        model = CGM24_workflow.main()
    else:
        raise Exception(
            "The pyCMG processing type is not implemented, you selected %s" % pyCGM_processing_type)

    # --------------------------Reporting -----------------------
    webReportFlag = toBool(str(session_xml.find("Create_WEB_report").text))
    pdfReportFlag = toBool(str(session_xml.find("Create_PDF_report").text))

    if webReportFlag:
        create_web_report(session_xml, processed_folder)
    if pdfReportFlag:
        create_pdf_report(session_xml, processed_folder, model)
