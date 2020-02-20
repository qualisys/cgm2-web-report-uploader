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


def CGM1_workflow(sessionXML, work_folder):
    file = "session.xml"
    sessionDate = utils.get_creation_date(sessionXML)
    # ---------------------------------------------------------------------------
    # management of the Processed folder
    DATA_PATH = os.path.join(work_folder, "processed")
    files.createDir(DATA_PATH)

    staticMeasurement = qtmTools.findStatic(sessionXML)
    filename = qtmTools.getFilename(staticMeasurement)
    calibrated_file_path = os.path.join(DATA_PATH, filename)
    if not os.path.isfile(calibrated_file_path):
        shutil.copyfile(os.path.join(work_folder, filename),
                        calibrated_file_path)
        logging.info("qualisys exported c3d file [%s] copied to processed folder" % (
            filename))

    dynamicMeasurements = qtmTools.findDynamic(sessionXML)
    for dynamicMeasurement in dynamicMeasurements:
        filename = qtmTools.getFilename(dynamicMeasurement)
        no_events_file_path = os.path.join(work_folder, filename)
        processed_file_path = os.path.join(DATA_PATH, filename)
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

    # --------------------------GLOBAL SETTINGS ------------------------------------
    # global setting ( in user/AppData)

    if os.path.isfile(pyCGM2.PYCGM2_APPDATA_PATH + "CGM1-pyCGM2.settings"):
        settings = files.openFile(
            pyCGM2.PYCGM2_APPDATA_PATH, "CGM1-pyCGM2.settings")
    else:
        settings = files.openFile(
            pyCGM2.PYCGM2_SETTINGS_FOLDER, "CGM1-pyCGM2.settings")

    # --------------------------MP ------------------------------------
    required_mp, optional_mp = qtmTools.SubjectMp(sessionXML)

    #  translators management
    translators = files.getTranslators(work_folder+"\\", "CGM1.translators")
    if not translators:
        translators = settings["Translators"]

    # --------------------------MODEL CALIBRATION -----------------------
    staticMeasurement = qtmTools.findStatic(sessionXML)
    calibrateFilenameLabelled = qtmTools.getFilename(staticMeasurement)
    leftFlatFoot = toBool(staticMeasurement.Left_foot_flat)
    rightFlatFoot = toBool(staticMeasurement.Right_foot_flat)
    headFlat = toBool(staticMeasurement.Head_flat)
    markerDiameter = float(staticMeasurement.Marker_diameter.text)*1000.0
    pointSuffix = None

    model, _ = cgm1.calibrate(DATA_PATH + "\\", calibrateFilenameLabelled, translators,
                              required_mp, optional_mp,
                              leftFlatFoot, rightFlatFoot, headFlat, markerDiameter,
                              pointSuffix)

    # --------------------------MODEL FITTING -----------------------
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)

    modelledC3ds = []
    for dynamicMeasurement in dynamicMeasurements:

        reconstructFilenameLabelled = qtmTools.getFilename(dynamicMeasurement)
        logging.info("----Processing of [%s]-----" %
                     (reconstructFilenameLabelled))
        mfpa = qtmTools.getForcePlateAssigment(dynamicMeasurement)
        momentProjection = enums.MomentProjection.Distal

        # filtering
        file_path = os.path.join(DATA_PATH, reconstructFilenameLabelled)
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

        btkTools.smartWriter(file_path)

        acqGait = cgm1.fitting(model, DATA_PATH + "\\", reconstructFilenameLabelled,
                               translators,
                               markerDiameter,
                               pointSuffix,
                               mfpa, momentProjection)

        btkTools.smartWriter(acqGait, file_path)
        modelledC3ds.append(reconstructFilenameLabelled)

    # --------------------------GAIT PROCESSING -----------------------
    webReportFlag = toBool(str(sessionXML.find("Create_WEB_report").text))
    pdfReportFlag = toBool(str(sessionXML.find("Create_PDF_report").text))

    if webReportFlag or pdfReportFlag:
        nds = normativeDatasets.Schwartz2008("Free")

        types = qtmTools.detectMeasurementType(sessionXML)
        for type in types:

            modelledTrials = []
            for dynamicMeasurement in dynamicMeasurements:
                if qtmTools.isType(dynamicMeasurement, type):
                    filename = qtmTools.getFilename(dynamicMeasurement)
                    modelledTrials.append(filename)

            subjectMd = {"patientName": sessionXML.find("Last_name").text + " " + sessionXML.find("First_name").text,
                         "bodyHeight": sessionXML.find("Height").text,
                         "bodyWeight": sessionXML.find("Weight").text,
                         "diagnosis": sessionXML.find("Diagnosis").text,
                         "dob": sessionXML.find("Date_of_birth").text,
                         "sex": sessionXML.find("Sex").text,
                         "test condition": type,
                         "gmfcs": sessionXML.find("Gross_Motor_Function_Classification").text,
                         "fms": sessionXML.find("Functional_Mobility_Scale").text}

            if webReportFlag:
                report = qtmFilters.WebReportFilter(
                    DATA_PATH, modelledTrials, subjectMd, sessionDate)
                # report.exportJson()
                save_session_data_xml_from(report.getReportData())
                report.upload()
                logging.info("qualisys Web Report exported")

            if pdfReportFlag:

                analysisInstance = analysis.makeAnalysis(
                    DATA_PATH, modelledTrials,
                    subjectInfo=None,
                    experimentalInfo=None,
                    modelInfo=None,
                    pointLabelSuffix=None)

                title = type

                # spatiotemporal
                plot.plot_spatioTemporal(DATA_PATH, analysisInstance,
                                         exportPdf=True,
                                         outputName=title,
                                         show=None,
                                         title=title)

                # Kinematics
                if model.m_bodypart in [enums.BodyPart.LowerLimb, enums.BodyPart.LowerLimbTrunk, enums.BodyPart.FullBody]:
                    plot.plot_DescriptiveKinematic(DATA_PATH, analysisInstance, "LowerLimb",
                                                   nds,
                                                   exportPdf=True,
                                                   outputName=title,
                                                   pointLabelSuffix=pointSuffix,
                                                   show=False,
                                                   title=title)

                    plot.plot_ConsistencyKinematic(DATA_PATH, analysisInstance, "LowerLimb",
                                                   nds,
                                                   exportPdf=True,
                                                   outputName=title,
                                                   pointLabelSuffix=pointSuffix,
                                                   show=False,
                                                   title=title)
                if model.m_bodypart in [enums.BodyPart.LowerLimbTrunk, enums.BodyPart.FullBody]:
                    plot.plot_DescriptiveKinematic(DATA_PATH, analysisInstance, "Trunk",
                                                   nds,
                                                   exportPdf=True,
                                                   outputName=title,
                                                   pointLabelSuffix=pointSuffix,
                                                   show=False,
                                                   title=title)

                    plot.plot_ConsistencyKinematic(DATA_PATH, analysisInstance, "Trunk",
                                                   nds,
                                                   exportPdf=True,
                                                   outputName=title,
                                                   pointLabelSuffix=pointSuffix,
                                                   show=False,
                                                   title=title)

                if model.m_bodypart in [enums.BodyPart.UpperLimb, enums.BodyPart.FullBody]:
                    pass  # TODO plot upperlimb panel

                # Kinetics
                if model.m_bodypart in [enums.BodyPart.LowerLimb, enums.BodyPart.LowerLimbTrunk, enums.BodyPart.FullBody]:
                    plot.plot_DescriptiveKinetic(DATA_PATH, analysisInstance, "LowerLimb",
                                                 nds,
                                                 exportPdf=True,
                                                 outputName=title,
                                                 pointLabelSuffix=pointSuffix,
                                                 show=False,
                                                 title=title)

                    plot.plot_ConsistencyKinetic(DATA_PATH, analysisInstance, "LowerLimb",
                                                 nds,
                                                 exportPdf=True,
                                                 outputName=title,
                                                 pointLabelSuffix=pointSuffix,
                                                 show=False,
                                                 title=title)

                # MAP
                plot.plot_MAP(DATA_PATH, analysisInstance,
                              nds,
                              exportPdf=True,
                              outputName=title, pointLabelSuffix=pointSuffix,
                              show=False,
                              title=title)

                plt.show()


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
