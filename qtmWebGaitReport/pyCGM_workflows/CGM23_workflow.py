# -*- coding: utf-8 -*-
from pyCGM2 import log
from qtmWebGaitReport import qtmFilters
from pyCGM2.Inspect import inspectFilters, inspectProcedures
import argparse
import matplotlib.pyplot as plt
import logging
import os
import shutil

import pyCGM2
from pyCGM2.Model.CGM2 import cgm, cgm2
from pyCGM2.Lib.CGM import cgm2_3
from pyCGM2.Utils import files
from pyCGM2.Utils.utils import *
from pyCGM2.qtm import qtmTools
from qtmWebGaitReport import utils
from pyCGM2 import enums
from pyCGM2.Tools import btkTools
from pyCGM2.Lib import eventDetector, analysis, plot
from pyCGM2.Report import normativeDatasets
from pyCGM2.Signal import signal_processing
from pyCGM2.ForcePlates import forceplates
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


log.setLogger(level=logging.INFO)
with open('pyCGM2.log', 'w'):
    pass


MARKERSETS = {"Lower limb tracking markers": cgm2.CGM2_3.LOWERLIMB_TRACKING_MARKERS,
              "Thorax tracking markers": cgm.CGM1.THORAX_TRACKING_MARKERS,
              "Upper limb tracking markers": cgm.CGM1.UPPERLIMB_TRACKING_MARKERS,
              "Calibration markers": ["LKNM", "RKNM", "LMED", "RMED", "LKAX", "LKD1", "LKD2", "RKAX", "RKD1", "RKD2"]}


def main():

    logging.info("------------------------------------------------")
    logging.info("------------QTM - pyCGM2 Workflow---------------")
    logging.info("------------------------------------------------")
    file = "session.xml"
    sessionXML = files.readXml(os.getcwd()+"\\", file)
    sessionDate = files.getFileCreationDate(os.getcwd()+"\\"+file)

    # ---------------------------------------------------------------------------
    # management of the Processed folder
    DATA_PATH = os.getcwd()+"\\"+"processed\\"
    files.createDir(DATA_PATH)

    staticMeasurement = utils.find_static(sessionXML)
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

            if btkTools.checkForcePlateExist(acq):
                if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
                    forceplates.correctForcePlateType5(acq)

            acq, zeniState = eventDetector.zeni(acq)

            if zeniState:
                btkTools.smartWriter(
                    acq, str(DATA_PATH + reconstructFilenameLabelled))

                cmd = "Mokka.exe \"%s\"" % (
                    str(DATA_PATH + reconstructFilenameLabelled))
                os.system(cmd)

    # --------------------------GLOBAL SETTINGS ------------------------------------
    # global setting ( in user/AppData)

    if os.path.isfile(pyCGM2.PYCGM2_APPDATA_PATH + "CGM2_3-pyCGM2.settings"):
        settings = files.openFile(
            pyCGM2.PYCGM2_APPDATA_PATH, "CGM2_3-pyCGM2.settings")
    else:
        settings = files.openFile(
            pyCGM2.PYCGM2_SETTINGS_FOLDER, "CGM2_3-pyCGM2.settings")
    # --------------------------MP ------------------------------------
    required_mp, optional_mp = qtmTools.SubjectMp(sessionXML)

    # --Check MP
    inspectprocedure = inspectProcedures.AnthropometricDataQualityProcedure(
        required_mp)
    inspector = inspectFilters.QualityFilter(inspectprocedure)
    inspector.run()

    #  translators management
    translators = files.getTranslators(os.getcwd()+"\\", "CGM2_3.translators")
    if not translators:
        translators = settings["Translators"]

    #  ikweight
    ikWeight = files.getIKweightSet(DATA_PATH, "CGM2_3.ikw")
    if not ikWeight:
        ikWeight = settings["Fitting"]["Weight"]

    # --------------------------MODEL CALIBRATION -----------------------
    logging.info(
        "--------------------------MODEL CALIBRATION -----------------------")
    staticMeasurement = utils.find_static(sessionXML)
    calibrateFilenameLabelled = qtmTools.getFilename(staticMeasurement)

    logging.info(
        "----- CALIBRATION-  static file [%s]--" % (calibrateFilenameLabelled))

    leftFlatFoot = toBool(
        staticMeasurement.Left_foot_normalised_to_static_trial.text)
    rightFlatFoot = toBool(
        staticMeasurement.Right_foot_normalised_to_static_trial.text)
    headFlat = toBool(staticMeasurement.Head_normalised_to_static_trial.text)

    markerDiameter = float(staticMeasurement.Marker_diameter.text)*1000.0
    hjcMethod = settings["Calibration"]["HJC"]

    pointSuffix = None

    # Calibration checking
    # --------------------
    acqStatic = btkTools.smartReader(DATA_PATH+calibrateFilenameLabelled)
    for key in MARKERSETS.keys():
        logging.info("[pyCGM2] Checking of the %s" % (key))

        # presence
        ip_presence = inspectProcedures.MarkerPresenceQualityProcedure(acqStatic,
                                                                       markers=MARKERSETS[key])
        inspector = inspectFilters.QualityFilter(ip_presence)
        inspector.run()

        if ip_presence.markersIn != []:

            ip_gap = inspectProcedures.GapQualityProcedure(acqStatic,
                                                           markers=ip_presence.markersIn)
            inspector = inspectFilters.QualityFilter(ip_gap)
            inspector.run()

            ip_swap = inspectProcedures.SwappingMarkerQualityProcedure(acqStatic,
                                                                       markers=ip_presence.markersIn)
            inspector = inspectFilters.QualityFilter(ip_swap)
            inspector.run()

            ip_pos = inspectProcedures.MarkerPositionQualityProcedure(acqStatic,
                                                                      markers=ip_presence.markersIn)
            inspector = inspectFilters.QualityFilter(ip_pos)

    # Calibration operation
    # --------------------
    logging.info("[pyCGM2] --- calibration operation ---")
    model, acqStatic = cgm2_3.calibrate(DATA_PATH,
                                        calibrateFilenameLabelled,
                                        translators, settings,
                                        required_mp, optional_mp,
                                        False,
                                        leftFlatFoot, rightFlatFoot, headFlat, markerDiameter,
                                        hjcMethod,
                                        pointSuffix)

    logging.info(
        "----- CALIBRATION-  static file [%s]-----> DONE" % (calibrateFilenameLabelled))

    # --------------------------MODEL FITTING ----------------------------------
    logging.info(
        "--------------------------MODEL FITTING ----------------------------------")
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)

    ik_flag = True

    modelledC3ds = list()
    eventInspectorStates = list()
    for dynamicMeasurement in dynamicMeasurements:

        # reconstructFilenameLabelled = qtmTools.getFilename(dynamicMeasurement)
        reconstructFilenameLabelled = qtmTools.getFilename(dynamicMeasurement)

        logging.info("----Processing of [%s]-----" %
                     (reconstructFilenameLabelled))
        mfpa = qtmTools.getForcePlateAssigment(dynamicMeasurement)
        momentProjection_text = dynamicMeasurement.Moment_Projection.text
        if momentProjection_text == "Default":
            momentProjection_text = settings["Fitting"]["Moment Projection"]
        if momentProjection_text == "Distal":
            momentProjection = enums.MomentProjection.Distal
        elif momentProjection_text == "Proximal":
            momentProjection = enums.MomentProjection.Proximal
        elif momentProjection_text == "Global":
            momentProjection = enums.MomentProjection.Global
        elif momentProjection_text == "JCS":
            momentProjection = enums.MomentProjection.JCS

        acq = btkTools.smartReader(DATA_PATH+reconstructFilenameLabelled)

        # Fitting checking
        # --------------------
        for key in MARKERSETS.keys():
            if key != "Calibration markers":

                logging.info("[pyCGM2] Checking of the %s" % (key))
                # presence
                ip_presence = inspectProcedures.MarkerPresenceQualityProcedure(acq,
                                                                               markers=MARKERSETS[key])
                inspector = inspectFilters.QualityFilter(ip_presence)
                inspector.run()

                if ip_presence.markersIn != []:

                    ip_gap = inspectProcedures.GapQualityProcedure(acq,
                                                                   markers=ip_presence.markersIn)
                    inspector = inspectFilters.QualityFilter(ip_gap)
                    inspector.run()

                    ip_swap = inspectProcedures.SwappingMarkerQualityProcedure(acq,
                                                                               markers=ip_presence.markersIn)
                    inspector = inspectFilters.QualityFilter(ip_swap)
                    inspector.run()

                    ip_pos = inspectProcedures.MarkerPositionQualityProcedure(acq,
                                                                              markers=ip_presence.markersIn)
                    inspector = inspectFilters.QualityFilter(ip_pos)

        # filtering
        # -----------------------

        # marker
        order = int(float(dynamicMeasurement.Marker_lowpass_filter_order.text))
        fc = float(dynamicMeasurement.Marker_lowpass_filter_frequency.text)

        signal_processing.markerFiltering(acq, order=order, fc=fc)

        # management of force plate type 5 and force plate filtering
        order = int(
            float(dynamicMeasurement.Forceplate_lowpass_filter_order.text))
        fc = float(dynamicMeasurement.Forceplate_lowpass_filter_frequency.text)

        if order != 0 and fc != 0:
            acq = btkTools.smartReader(DATA_PATH+reconstructFilenameLabelled)
            if btkTools.checkForcePlateExist(acq):
                if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
                    forceplates.correctForcePlateType5(acq)
            signal_processing.markerFiltering(acq, order=order, fc=fc)
        else:
            if btkTools.checkForcePlateExist(acq):
                if "5" in btkTools.smartGetMetadata(acq, "FORCE_PLATFORM", "TYPE"):
                    forceplates.correctForcePlateType5(acq)

        btkTools.smartWriter(acq, DATA_PATH+reconstructFilenameLabelled)

        # event checking
        # -----------------------
        inspectprocedureEvents = inspectProcedures.GaitEventQualityProcedure(
            acq)
        inspector = inspectFilters.QualityFilter(inspectprocedureEvents)
        inspector.run()
        eventInspectorStates.append(inspectprocedureEvents.state)

        # fitting operation
        # -----------------------
        logging.info("[pyCGM2] --- Fitting operation ---")
        acqGait = cgm2_3.fitting(model, DATA_PATH, reconstructFilenameLabelled,
                                 translators, settings,
                                 ik_flag, markerDiameter,
                                 pointSuffix,
                                 mfpa,
                                 momentProjection)

        outFilename = reconstructFilenameLabelled  # [:-4] + "_CGM1.c3d"
        btkTools.smartWriter(acqGait, str(DATA_PATH + outFilename))
        modelledC3ds.append(outFilename)

        logging.info("----Processing of [%s]-----> DONE" %
                     (reconstructFilenameLabelled))

    # --------------------------GAIT PROCESSING -----------------------
    if not all(eventInspectorStates):
        raise Exception(
            "[pyCGM2] Impossible to run Gait processing. Badly gait event detection. check the log file")
    logging.info(
        "---------------------GAIT PROCESSING -----------------------")
    return model


if __name__ == "__main__":

    main()
