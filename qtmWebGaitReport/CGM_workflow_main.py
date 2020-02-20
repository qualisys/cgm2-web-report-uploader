# -*- coding: utf-8 -*-
import pyCGM2
from pyCGM2 import log
from pyCGM2.Lib import eventDetector, analysis, plot
from pyCGM2.ForcePlates import forceplates
from pyCGM2.Signal import signal_processing
from pyCGM2.Report import normativeDatasets
from pyCGM2.Tools import btkTools
from pyCGM2 import enums
from pyCGM2.qtm import qtmTools
from pyCGM2.Utils.utils import *
from pyCGM2.Utils import files
from pyCGM2.Lib.CGM import cgm1
from qtmWebGaitReport import qtmFilters
from qtmWebGaitReport.convert_report_json_to_regression_test_xml import save_session_data_xml_from
from qtmWebGaitReport import utils
import shutil
import argparse
import matplotlib.pyplot as plt
import logging
import warnings
import os

log.setLoggingLevel(logging.INFO)

warnings.simplefilter(action='ignore', category=FutureWarning)


def create_pdf_report(data_path, modelled_trials, title, model, point_suffix, normative_dataset):
    analysisInstance = analysis.makeAnalysis(
        data_path, modelled_trials,
        subjectInfo=None,
        experimentalInfo=None,
        modelInfo=None,
        pointLabelSuffix=None)

    # spatiotemporal
    plot.plot_spatioTemporal(data_path, analysisInstance,
                             exportPdf=True,
                             outputName=title,
                             show=None,
                             title=title)

    # Kinematics
    if model.m_bodypart in [enums.BodyPart.LowerLimb, enums.BodyPart.LowerLimbTrunk, enums.BodyPart.FullBody]:
        plot.plot_DescriptiveKinematic(data_path, analysisInstance, "LowerLimb",
                                       normative_dataset,
                                       exportPdf=True,
                                       outputName=title,
                                       pointLabelSuffix=point_suffix,
                                       show=False,
                                       title=title)

        plot.plot_ConsistencyKinematic(data_path, analysisInstance, "LowerLimb",
                                       normative_dataset,
                                       exportPdf=True,
                                       outputName=title,
                                       pointLabelSuffix=point_suffix,
                                       show=False,
                                       title=title)
    if model.m_bodypart in [enums.BodyPart.LowerLimbTrunk, enums.BodyPart.FullBody]:
        plot.plot_DescriptiveKinematic(data_path, analysisInstance, "Trunk",
                                       normative_dataset,
                                       exportPdf=True,
                                       outputName=title,
                                       pointLabelSuffix=point_suffix,
                                       show=False,
                                       title=title)

        plot.plot_ConsistencyKinematic(data_path, analysisInstance, "Trunk",
                                       normative_dataset,
                                       exportPdf=True,
                                       outputName=title,
                                       pointLabelSuffix=point_suffix,
                                       show=False,
                                       title=title)

    if model.m_bodypart in [enums.BodyPart.UpperLimb, enums.BodyPart.FullBody]:
        pass  # TODO plot upperlimb panel

    # Kinetics
    if model.m_bodypart in [enums.BodyPart.LowerLimb, enums.BodyPart.LowerLimbTrunk, enums.BodyPart.FullBody]:
        plot.plot_DescriptiveKinetic(data_path, analysisInstance, "LowerLimb",
                                     normative_dataset,
                                     exportPdf=True,
                                     outputName=title,
                                     pointLabelSuffix=point_suffix,
                                     show=False,
                                     title=title)

        plot.plot_ConsistencyKinetic(data_path, analysisInstance, "LowerLimb",
                                     normative_dataset,
                                     exportPdf=True,
                                     outputName=title,
                                     pointLabelSuffix=point_suffix,
                                     show=False,
                                     title=title)

    # MAP
    plot.plot_MAP(data_path, analysisInstance,
                  normative_dataset,
                  exportPdf=True,
                  outputName=title, pointLabelSuffix=point_suffix,
                  show=False,
                  title=title)

    plt.show()


def fetch_translators(work_folder):
    if os.path.isfile(pyCGM2.PYCGM2_APPDATA_PATH + "CGM1-pyCGM2.settings"):
        settings = files.openFile(
            pyCGM2.PYCGM2_APPDATA_PATH, "CGM1-pyCGM2.settings")
    else:
        settings = files.openFile(
            pyCGM2.PYCGM2_SETTINGS_FOLDER, "CGM1-pyCGM2.settings")

    #  translators management
    translators = files.getTranslators(work_folder+"\\", "CGM1.translators")
    if not translators:
        translators = settings["Translators"]
    return translators


def get_model_and_fit_to_measurements(sessionXML, data_path, translators, required_mp, optional_mp, point_suffix):
    staticMeasurement = qtmTools.findStatic(sessionXML)
    calibrateFilenameLabelled = qtmTools.getFilename(staticMeasurement)
    leftFlatFoot = toBool(staticMeasurement.Left_foot_flat)
    rightFlatFoot = toBool(staticMeasurement.Right_foot_flat)
    headFlat = toBool(staticMeasurement.Head_flat)
    markerDiameter = float(staticMeasurement.Marker_diameter.text)*1000.0

    model, _ = cgm1.calibrate(data_path + "\\", calibrateFilenameLabelled, translators,
                              required_mp, optional_mp,
                              leftFlatFoot, rightFlatFoot, headFlat, markerDiameter,
                              point_suffix)

    # --------------------------MODEL FITTING -----------------------
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)

    modelledC3ds = []
    for dynamicMeasurement in dynamicMeasurements:

        filename = qtmTools.getFilename(dynamicMeasurement)
        logging.info("----Processing of [%s]-----" % filename)
        mfpa = qtmTools.getForcePlateAssigment(dynamicMeasurement)
        momentProjection = enums.MomentProjection.Distal

        # filtering
        file_path = os.path.join(data_path, filename)
        acq = btkTools.smartReader(file_path)
        if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
            forceplates.correctForcePlateType5(acq)

        # marker
        order = int(float(dynamicMeasurement.Marker_lowpass_filter_order.text))
        fc = float(dynamicMeasurement.Marker_lowpass_filter_frequency.text)

        signal_processing.markerFiltering(acq, order=order, fc=fc)

        # force plate filtering
        order = int(
            float(dynamicMeasurement.Forceplate_lowpass_filter_order.text))
        fc = float(dynamicMeasurement.Forceplate_lowpass_filter_frequency.text)

        if order != 0 and fc != 0:
            acq = btkTools.smartReader(file_path)
            if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
                forceplates.correctForcePlateType5(acq)
            signal_processing.markerFiltering(acq, order=order, fc=fc)

        btkTools.smartWriter(acq, file_path)

        acqGait = cgm1.fitting(model, data_path + "\\", filename,
                               translators,
                               markerDiameter,
                               point_suffix,
                               mfpa, momentProjection)

        btkTools.smartWriter(acqGait, file_path)
        modelledC3ds.append(filename)
    return model


def prepare_processed_folder(sessionXML, work_folder, processed_folder):
    files.createDir(processed_folder)

    staticMeasurement = qtmTools.findStatic(sessionXML)
    filename = qtmTools.getFilename(staticMeasurement)
    calibrated_file_path = os.path.join(processed_folder, filename)
    if not os.path.isfile(calibrated_file_path):
        shutil.copyfile(os.path.join(work_folder, filename),
                        calibrated_file_path)
        logging.info("qualisys exported c3d file [%s] copied to processed folder" % (
            filename))

    dynamicMeasurements = qtmTools.findDynamic(sessionXML)
    for dynamicMeasurement in dynamicMeasurements:
        filename = qtmTools.getFilename(dynamicMeasurement)
        no_events_file_path = os.path.join(work_folder, filename)
        processed_file_path = os.path.join(processed_folder, filename)
        if not os.path.isfile(processed_file_path):
            shutil.copyfile(no_events_file_path,
                            processed_file_path)
            logging.info("qualisys exported c3d file [%s] copied to processed folder" % (
                filename))

            acq = btkTools.smartReader(processed_file_path)
            if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
                forceplates.correctForcePlateType5(acq)
            acq = eventDetector.zeni(acq)
            btkTools.smartWriter(acq, processed_file_path)

            cmd = "Mokka.exe \"%s\"" % (processed_file_path)
            os.system(cmd)


def get_modelled_trials(session_xml, measurement_type):
    modelled_trials = []
    dynamicMeasurements = qtmTools.findDynamic(session_xml)
    for dynamicMeasurement in dynamicMeasurements:
        if qtmTools.isType(dynamicMeasurement, measurement_type):
            filename = qtmTools.getFilename(dynamicMeasurement)
            modelled_trials.append(filename)
    return modelled_trials


def create_web_report(session_xml, data_path):

    measurement_types = qtmTools.detectMeasurementType(session_xml)
    for measurement_type in measurement_types:

        modelledTrials = get_modelled_trials(session_xml, measurement_type)

        subjectMd = {"patientName": session_xml.find("Last_name").text + " " + session_xml.find("First_name").text,
                     "bodyHeight": session_xml.find("Height").text,
                     "bodyWeight": session_xml.find("Weight").text,
                     "diagnosis": session_xml.find("Diagnosis").text,
                     "dob": session_xml.find("Date_of_birth").text,
                     "sex": session_xml.find("Sex").text,
                     "test condition": measurement_type,
                     "gmfcs": session_xml.find("Gross_Motor_Function_Classification").text,
                     "fms": session_xml.find("Functional_Mobility_Scale").text}

        sessionDate = utils.get_creation_date(session_xml)

        report = qtmFilters.WebReportFilter(
            data_path, modelledTrials, subjectMd, sessionDate)
        # report.exportJson()
        save_session_data_xml_from(report.getReportData())
        report.upload()
        logging.info("qualisys Web Report exported")


def create_pdf_report(session_xml, data_path, model, point_suffix):
    normative_dataset = normativeDatasets.Schwartz2008("Free")
    measurement_types = qtmTools.detectMeasurementType(session_xml)
    for measurement_type in measurement_types:

        modelledTrials = get_modelled_trials(session_xml, measurement_type)
        create_pdf_report(
            data_path, modelledTrials, measurement_type, model, point_suffix, normative_dataset)


def CGM1_workflow(session_xml, work_folder):

    # ---------------------------------------------------------------------------
    # management of the Processed folder
    processed_folder = os.path.join(work_folder, "processed")

    prepare_processed_folder(session_xml, work_folder, processed_folder)

    translators = fetch_translators(work_folder)
    required_mp, optional_mp = qtmTools.SubjectMp(session_xml)
    point_suffix = None

    model = get_model_and_fit_to_measurements(
        session_xml, processed_folder, translators, required_mp, optional_mp, point_suffix)

    # --------------------------Reporting -----------------------
    webReportFlag = toBool(str(session_xml.find("Create_WEB_report").text))
    pdfReportFlag = toBool(str(session_xml.find("Create_PDF_report").text))

    if webReportFlag:
        create_web_report(session_xml)
    if pdfReportFlag:
        create_pdf_report(session_xml, processed_folder, model, point_suffix)


def CGM23_workflow(sessionXML):
    pass


def main():
    work_folder = os.getcwd()
    session_xml_path = os.path.join(work_folder, "session.xml")
    sessionXML = utils.read_session_xml(session_xml_path)
    pyCGM_processing_type = sessionXML.Subsession.pyCGM_Processing_Type.text

    if pyCGM_processing_type == "pyCGM1":
        CGM1_workflow(sessionXML, work_folder)
    elif pyCGM_processing_type == "pyCGM23":
        CGM23_workflow(sessionXML)
    else:
        raise Exception(
            "Only pyCGM1 processing is currently implemented, but you selected %s" % pyCGM_processing_type)
