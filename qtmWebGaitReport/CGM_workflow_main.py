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
from pyCGM2.Lib.CGM import cgm2_3
from pyCGM2.Configurator import ModelManager
from qtmWebGaitReport import qtmFilters
from qtmWebGaitReport.pyCGM_workflows import CGM1_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM11_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM21_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM22_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM23_workflow
from qtmWebGaitReport.pyCGM_workflows import CGM24_workflow
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


def filter_data(file_path, measurement):
    acq = btkTools.smartReader(file_path)
    if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
        forceplates.correctForcePlateType5(acq)

    # marker
    order = int(float(measurement.Marker_lowpass_filter_order.text))
    fc = float(measurement.Marker_lowpass_filter_frequency.text)

    signal_processing.markerFiltering(acq, order=order, fc=fc)

    # force plate filtering
    order = int(float(measurement.Forceplate_lowpass_filter_order.text))
    fc = float(measurement.Forceplate_lowpass_filter_frequency.text)

    if order != 0 and fc != 0:
        acq = btkTools.smartReader(file_path)
        if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
            forceplates.correctForcePlateType5(acq)
        signal_processing.markerFiltering(acq, order=order, fc=fc)

    btkTools.smartWriter(acq, file_path)


def get_processing_module_alias(model_type):
    if model_type == "CGM1":
        proccessing_module = cgm1
    elif model_type == "CGM2_3":
        proccessing_module = cgm2_3
    else:
        raise Exception(
            "Processing for model_type={} is not implemented".format(model_type))
    return proccessing_module


def get_settings(version):
    if os.path.isfile(pyCGM2.PYCGM2_APPDATA_PATH + "%s-pyCGM2.settings" % version):
        settings = files.openFile(
            pyCGM2.PYCGM2_APPDATA_PATH, "%s-pyCGM2.settings" % version)
    else:
        settings = files.openFile(
            pyCGM2.PYCGM2_SETTINGS_FOLDER, "%s-pyCGM2.settings" % version)
    return settings


def get_calibration_arguments_and_model_manager(model_type, data_path, session_xml, point_suffix):
    settings = get_settings(model_type)
    translators = settings["Translators"]
    required_mp, optional_mp = qtmTools.SubjectMp(session_xml)

    static_session_xml_soup = qtmTools.findStatic(session_xml)
    calibration_filename = qtmTools.getFilename(static_session_xml_soup)

    leftFlatFoot = toBool(static_session_xml_soup.Left_foot_flat)
    rightFlatFoot = toBool(static_session_xml_soup.Right_foot_flat)
    headFlat = toBool(static_session_xml_soup.Head_flat)
    markerDiameter = float(
        static_session_xml_soup.Marker_diameter.text)*1000.0

    dynamic_measurements = qtmTools.findDynamic(session_xml)
    user_settings = {
        "Calibration": {
            "Left flat foot": leftFlatFoot,
            "Right flat foot": rightFlatFoot,
            "Head flat": headFlat,
            "StaticTrial": calibration_filename
        },
        "Global": {
            "Marker diameter": markerDiameter,
            "Point suffix": point_suffix
        },
        "MP": {
            "Required": required_mp,
            "Optional": optional_mp
        },
        "Fitting": {
            "Trials": dynamic_measurements
        }
    }
    if model_type == "CGM1":
        model_manager = ModelManager.CGM1ConfigManager(
            user_settings, localInternalSettings=settings, localTranslators={"Translators": translators})
        model_manager.contruct()
        calibration_arguments = (
            data_path + "\\",
            model_manager.staticTrial,
            model_manager.translators,
            model_manager.requiredMp,
            model_manager.optionalMp,
            model_manager.leftFlatFoot,
            model_manager.rightFlatFoot,
            model_manager.headFlat,
            model_manager.markerDiameter,
            model_manager.pointSuffix,
        )
    elif model_type == "CGM2_3":
        model_manager = ModelManager.CGM2_3ConfigManager(
            user_settings, localInternalSettings=settings, localTranslators={"Translators": translators})
        model_manager.contruct()
        finalSettings = model_manager.getFinalSettings()
        calibration_arguments = (
            data_path + "\\",
            model_manager.staticTrial,
            model_manager.translators,
            finalSettings,
            model_manager.requiredMp,
            model_manager.optionalMp,
            model_manager.enableIK,
            model_manager.leftFlatFoot,
            model_manager.rightFlatFoot,
            model_manager.headFlat,
            model_manager.markerDiameter,
            model_manager.hjcMethod,
            model_manager.pointSuffix,
        )
    else:
        raise Exception(
            "Processing for model_type={} is not implemented".format(model_type))
    return calibration_arguments, model_manager


def get_model_fitting_settings(model_type, dynamic_measurement, model, data_path, model_manager, point_suffix):
    if model_type == "CGM1":
        filename = qtmTools.getFilename(dynamic_measurement)
        mfpa = qtmTools.getForcePlateAssigment(dynamic_measurement)
        # momentProjection = enums.MomentProjection.Distal
        settings = (
            model, data_path + "\\",
            filename,
            model_manager.translators,
            model_manager.markerDiameter,
            model_manager.pointSuffix,
            mfpa,
            model_manager.momentProjection
        )
    elif model_type == "CGM2_3":
        settings = ()
    else:
        raise Exception(
            "Processing for model_type={} is not implemented".format(model_type))
    return settings


def fit_model_to_measurements(model, model_type, model_manager, data_path, point_suffix):
    processing_module = get_processing_module_alias(model_type)
    for dynamic_measurement in model_manager.dynamicTrials:
        fitting_settings = get_model_fitting_settings(
            model_type, dynamic_measurement, model, data_path, model_manager, point_suffix)

        filename = qtmTools.getFilename(dynamic_measurement)
        logging.info("----Processing of [%s]-----" % filename)

        file_path = os.path.join(data_path, filename)
        filter_data(file_path, dynamic_measurement)

        acqGait = processing_module.fitting(*fitting_settings)

        btkTools.smartWriter(acqGait, file_path)


def get_model_and_fit_to_measurements(session_xml, data_path, model_type, point_suffix=None):

    calibration_args, model_manager = get_calibration_arguments_and_model_manager(
        model_type, data_path, session_xml, point_suffix)

    processing_module = get_processing_module_alias(model_type)
    model, _ = processing_module.calibrate(*calibration_args)

    fit_model_to_measurements(
        model, model_type, model_manager, data_path, point_suffix)

    return model


def get_modelled_trials(session_xml, measurement_type):
    modelled_trials = []
    dynamicMeasurements = qtmTools.findDynamic(session_xml)
    for dynamicMeasurement in dynamicMeasurements:
        if qtmTools.isType(dynamicMeasurement, measurement_type):
            filename = qtmTools.getFilename(dynamicMeasurement)
            modelled_trials.append(filename)
    return modelled_trials


def process_pdf_report(data_path, modelled_trials, title, model,  normative_dataset, point_suffix=None):
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


def create_subject_metadata(session_xml, measurement_type):
    return {
        "patientName": session_xml.find("Last_name").text + " " + session_xml.find("First_name").text,
        "patientID": session_xml.find("Patient_ID").text,
        "bodyHeight": session_xml.find("Height").text,
        "bodyWeight": session_xml.find("Weight").text,
        "diagnosis": session_xml.find("Diagnosis").text,
        "dob": session_xml.find("Date_of_birth").text,
        "sex": session_xml.find("Sex").text,
        "test condition": measurement_type,
        "gmfcs": session_xml.find("Gross_Motor_Function_Classification").text,
        "fms": session_xml.find("Functional_Mobility_Scale").text}


def create_web_report(session_xml, data_path):

    measurement_types = qtmTools.detectMeasurementType(session_xml)
    for measurement_type in measurement_types:

        modelledTrials = get_modelled_trials(session_xml, measurement_type)

        subjectMd = create_subject_metadata(session_xml, measurement_type)

        sessionDate = utils.get_creation_date(session_xml)

        report = qtmFilters.WebReportFilter(
            data_path, modelledTrials, subjectMd, sessionDate)
        # report.exportJson()
        save_session_data_xml_from(report.getReportData())
        report.upload()
        logging.info("qualisys Web Report exported")


def create_pdf_report(session_xml, data_path, model):
    normative_dataset = normativeDatasets.Schwartz2008("Free")
    measurement_types = qtmTools.detectMeasurementType(session_xml)
    for measurement_type in measurement_types:

        modelledTrials = get_modelled_trials(session_xml, measurement_type)
        process_pdf_report(
            data_path, modelledTrials, measurement_type, model, normative_dataset)


def run_CGM1_workflow_and_return_model(session_xml, processed_folder):
    model = get_model_and_fit_to_measurements(
        session_xml, processed_folder, model_type="CGM1")

    return model


def run_CGM23_workflow_and_return_model(session_xml, processed_folder):
    model = get_model_and_fit_to_measurements(
        session_xml, processed_folder, model_type="CGM2_3")
    return model


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
        CGM1_workflow.main()
    elif pyCGM_processing_type == "pyCGM11":
        CGM11_workflow.main()
    elif pyCGM_processing_type == "pyCGM21":
        CGM21_workflow.main()
    elif pyCGM_processing_type == "pyCGM22":
        CGM22_workflow.main()
    elif pyCGM_processing_type == "pyCGM23":
        # model = run_CGM23_workflow_and_return_model(
        #     session_xml, processed_folder)
        CGM23_workflow.main()
    elif pyCGM_processing_type == "pyCGM24":
        CGM24_workflow.main()
    else:
        raise Exception(
            "Only pyCGM1 processing is currently implemented, but you selected %s" % pyCGM_processing_type)

    # --------------------------Reporting -----------------------
    webReportFlag = toBool(str(session_xml.find("Create_WEB_report").text))
    pdfReportFlag = toBool(str(session_xml.find("Create_PDF_report").text))

    if webReportFlag:
        create_web_report(session_xml, processed_folder)
    if pdfReportFlag:
        create_pdf_report(session_xml, processed_folder, model)
