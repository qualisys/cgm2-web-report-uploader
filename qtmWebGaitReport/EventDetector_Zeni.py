# -*- coding: utf-8 -*-
import warnings
from pyCGM2.ForcePlates import forceplates
from pyCGM2.Lib import eventDetector
from pyCGM2.Tools import btkTools
from pyCGM2.qtm import qtmTools
from pyCGM2.Utils.utils import *
from qtmWebGaitReport import utils
import matplotlib.pyplot as plt
import logging
import os
import shutil
import pyCGM2
from pyCGM2 import log
log.setLoggingLevel(logging.INFO)


warnings.simplefilter(action='ignore', category=FutureWarning)


def prepare_folder_and_run_event_detection(sessionXML, work_folder, processed_folder):
    utils.create_directory_if_needed(processed_folder)

    staticMeasurement = utils.find_static(sessionXML)
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

            acq, state = eventDetector.zeni(acq)
            btkTools.smartWriter(acq, processed_file_path)


def verify_events_in_mokka(sessionXML, processed_folder):
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)
    for dynamicMeasurement in dynamicMeasurements:
        filename = qtmTools.getFilename(dynamicMeasurement)
        processed_file_path = os.path.join(processed_folder, filename)

        cmd = "Mokka.exe \"%s\"" % (processed_file_path)
        os.system(cmd)


def run_event_detection_and_verify_in_mokka(working_dir, processed_folder_name="processed"):

    session_xml_path = os.path.join(working_dir, "session.xml")
    sessionXML = utils.read_session_xml(session_xml_path)

    processed_data_path = os.path.join(working_dir, processed_folder_name)

    prepare_folder_and_run_event_detection(
        sessionXML, working_dir, processed_data_path)

    verify_events_in_mokka(sessionXML, processed_data_path)


def main():
    working_dir = os.getcwd()+"\\"
    run_event_detection_and_verify_in_mokka(working_dir)


if __name__ == "__main__":

    main()
