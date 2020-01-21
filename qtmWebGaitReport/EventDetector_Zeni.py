# -*- coding: utf-8 -*-
import warnings
from pyCGM2.ForcePlates import forceplates
from pyCGM2.Lib import eventDetector
from pyCGM2.Tools import btkTools
from pyCGM2.qtm import qtmTools
from pyCGM2.Utils.utils import *
from pyCGM2.Utils import files
import matplotlib.pyplot as plt
import logging
import os
import pyCGM2
from pyCGM2 import log
log.setLoggingLevel(logging.INFO)


warnings.simplefilter(action='ignore', category=FutureWarning)


def main():
    DATA_PATH = os.getcwd()+"\\"
    file = "session.xml"
    sessionXML = files.readXml(DATA_PATH, file)

    # create processed folder
    DATA_PATH_OUT = DATA_PATH + "processed\\"
    files.createDir(DATA_PATH_OUT)

    # --------------------------dynamic measurement-----------------------
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)

    # --------------------------EVENTS -----------------------
    for dynamicMeasurement in dynamicMeasurements:

        c3dfile = qtmTools.getFilename(dynamicMeasurement)

        logging.info("----Event detection of [%s]-----" % (c3dfile))
        acq = btkTools.smartReader(str(DATA_PATH+c3dfile))
        forcePlateType = btkTools.smartGetMetadata(
            acq, "FORCE_PLATFORM", "TYPE")
        if forcePlateType is not None and "5" in forcePlateType:
            forceplates.correctForcePlateType5(acq)

        acq = eventDetector.zeni(acq)
        btkTools.smartWriter(acq, str(DATA_PATH_OUT + c3dfile))

        cmd = "Mokka.exe \"%s\"" % (str(DATA_PATH_OUT + c3dfile))
        os.system(cmd)


if __name__ == "__main__":

    main()
