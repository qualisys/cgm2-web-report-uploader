# -*- coding: utf-8 -*-
from pyCGM2.Lib import eventDetector, analysis, plot
import warnings
from pyCGM2.ForcePlates import forceplates
from pyCGM2.Signal import signal_processing
from pyCGM2.Report import normativeDatasets
from pyCGM2.Tools import btkTools
from pyCGM2 import enums
from pyCGM2.qtm import qtmTools
from pyCGM2.Utils.utils import *
from pyCGM2.Utils import files
from pyCGM2.Lib.CGM import cgm1
import shutil
from qtmWebGaitReport import qtmFilters
import argparse
import matplotlib.pyplot as plt
import logging
import os
import pyCGM2
from pyCGM2 import log
log.setLoggingLevel(logging.INFO)

warnings.simplefilter(action='ignore', category=FutureWarning)


def main():
    file = "session.xml"
    sessionXML = files.readXml(os.getcwd()+"\\", file)
    sessionDate = files.getFileCreationDate(os.getcwd()+"\\"+file)

    # ---------------------------------------------------------------------------
    # management of the Processed folder
    DATA_PATH = os.getcwd()+"\\"+"processed\\"
    files.createDir(DATA_PATH)

    staticMeasurement = qtmTools.findStatic(sessionXML)
    calibrateFilenameLabelled = qtmTools.getFilename(staticMeasurement)
    if not os.path.isfile(DATA_PATH+calibrateFilenameLabelled):
        shutil.copyfile(os.getcwd()+"\\"+calibrateFilenameLabelled,
                        DATA_PATH+calibrateFilenameLabelled)
        logging.info("qualisys exported c3d file [%s] copied to processed folder" % (
            calibrateFilenameLabelled))

    dynamicMeasurements = qtmTools.findDynamic(sessionXML)
    for dynamicMeasurement in dynamicMeasurements:
        reconstructFilenameLabelled = qtmTools.getFilename(dynamicMeasurement)
        if not os.path.isfile(DATA_PATH+reconstructFilenameLabelled):
            shutil.copyfile(os.getcwd()+"\\"+reconstructFilenameLabelled,
                            DATA_PATH+reconstructFilenameLabelled)
            logging.info("qualisys exported c3d file [%s] copied to processed folder" % (
                reconstructFilenameLabelled))

            acq = btkTools.smartReader(
                str(DATA_PATH+reconstructFilenameLabelled))
            if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
                forceplates.correctForcePlateType5(acq)
            acq = eventDetector.zeni(acq)
            btkTools.smartWriter(
                acq, str(DATA_PATH + reconstructFilenameLabelled))

            cmd = "Mokka.exe \"%s\"" % (
                str(DATA_PATH + reconstructFilenameLabelled))
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
    translators = files.getTranslators(os.getcwd()+"\\", "CGM1.translators")
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

    model, _ = cgm1.calibrate(DATA_PATH, calibrateFilenameLabelled, translators,
                              required_mp, optional_mp,
                              leftFlatFoot, rightFlatFoot, headFlat, markerDiameter,
                              pointSuffix)

    # --------------------------MODEL FITTING -----------------------
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)

    modelledC3ds = list()
    for dynamicMeasurement in dynamicMeasurements:

        reconstructFilenameLabelled = qtmTools.getFilename(dynamicMeasurement)
        logging.info("----Processing of [%s]-----" %
                     (reconstructFilenameLabelled))
        mfpa = qtmTools.getForcePlateAssigment(dynamicMeasurement)
        momentProjection = enums.MomentProjection.Distal

        # filtering
        acq = btkTools.smartReader(DATA_PATH+reconstructFilenameLabelled)
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
            acq = btkTools.smartReader(DATA_PATH+reconstructFilenameLabelled)
            if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
                forceplates.correctForcePlateType5(acq)
            signal_processing.markerFiltering(acq, order=order, fc=fc)

        btkTools.smartWriter(acq, DATA_PATH+reconstructFilenameLabelled)

        acqGait = cgm1.fitting(model, DATA_PATH, reconstructFilenameLabelled,
                               translators,
                               markerDiameter,
                               pointSuffix,
                               mfpa, momentProjection)

        outFilename = reconstructFilenameLabelled
        btkTools.smartWriter(acqGait, str(DATA_PATH + outFilename))
        modelledC3ds.append(outFilename)

    # --------------------------GAIT PROCESSING -----------------------
    webReportFlag = toBool(str(sessionXML.find("Create_WEB_report").text))
    pdfReportFlag = toBool(str(sessionXML.find("Create_PDF_report").text))

    if webReportFlag or pdfReportFlag:
        nds = normativeDatasets.Schwartz2008("Free")

        types = qtmTools.detectMeasurementType(sessionXML)
        for type in types:

            modelledTrials = list()
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
                workingDirectory = DATA_PATH
                report = qtmFilters.WebReportFilter(
                    DATA_PATH, modelledTrials, subjectMd, sessionDate)
                # report.exportJson()
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


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='CGM1 workflow')

    args = parser.parse_args()

    main()
