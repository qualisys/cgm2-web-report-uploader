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
import pyCGM2
from pyCGM2 import log
log.setLoggingLevel(logging.INFO)


warnings.simplefilter(action='ignore', category=FutureWarning)


def main():
    working_dir = os.getcwd()+"\\"
    session_xml_path = os.path.join(working_dir, "session.xml")
    sessionXML = utils.read_session_xml(session_xml_path)

    # create processed folder
    processed_data_path = os.path.join(working_dir, "processed")
    utils.create_directory_if_needed(processed_data_path)

    # --------------------------dynamic measurement-----------------------
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)

    # --------------------------EVENTS -----------------------
    for dynamicMeasurement in dynamicMeasurements:

        c3dfile = qtmTools.getFilename(dynamicMeasurement)
        c3d_file_path = os.path.join(processed_data_path, c3dfile)

        logging.info("----Event detection of [%s]-----" % c3dfile)
        acq = btkTools.smartReader(c3d_file_path)
        forcePlateType = btkTools.smartGetMetadata(
            acq, "FORCE_PLATFORM", "TYPE")
        if forcePlateType is not None and "5" in forcePlateType:
            forceplates.correctForcePlateType5(acq)

        acq = eventDetector.zeni(acq)
        btkTools.smartWriter(acq, c3d_file_path)

        cmd = "Mokka.exe \"%s\"" % c3d_file_path
        os.system(cmd)


if __name__ == "__main__":

    main()
