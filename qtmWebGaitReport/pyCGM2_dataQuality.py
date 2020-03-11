# -*- coding: utf-8 -*-
from pyCGM2 import log
import logging
import os
import pyCGM2

from pyCGM2.Inspect import inspectFilters, inspectProcedures

from pyCGM2.Model.CGM2 import cgm, cgm2
from pyCGM2.Utils import files
from pyCGM2.Utils.utils import *
from pyCGM2.qtm import qtmTools
from qtmWebGaitReport import utils
from pyCGM2.Tools import btkTools

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


log.setLogger(filename="inspector.log", level=logging.INFO)
with open('inspector.log', 'w'):
    pass


def runAllQualityProcedures(folder, filenames):
    for filename in filenames:
        logging.info("--------file: [%s] --------" % (filename))
        logging.info("---------------------------")
        acq = btkTools.smartReader(os.path.join(
            folder, filename))

        all_procedures = [
            inspectProcedures.GapQualityProcedure,
            inspectProcedures.GaitEventQualityProcedure,
            inspectProcedures.SwappingMarkerQualityProcedure,
            inspectProcedures.MarkerPresenceQualityProcedure,
            inspectProcedures.MarkerPositionQualityProcedure,
        ]

        for procedureClass in all_procedures:
            procedureInstance = procedureClass(acq)
            inspector = inspectFilters.QualityFilter(procedureInstance)
            inspector.run()


def main():
    qtm_folder = os.getcwd()
    sessionXML = files.readXml(qtm_folder + "\\", "session.xml")

    # --------------------------MP ------------------------------------
    required_mp, _ = qtmTools.SubjectMp(sessionXML)

    # --------------------------Check MP ----------------------------------
    logging.info("--MP Checking--")
    inspectprocedure1 = inspectProcedures.AnthropometricDataQualityProcedure(
        required_mp)
    inspector = inspectFilters.QualityFilter(inspectprocedure1)
    inspector.run()

    # --------------------------FILES -----------------------
    staticMeasurement = utils.find_static(sessionXML)
    staticFilename = qtmTools.getFilename(staticMeasurement)

    dynamicFilenames = []
    dynamicMeasurements = qtmTools.findDynamic(sessionXML)
    for dynamicMeasurement in dynamicMeasurements:
        reconstructFilenameLabelled = qtmTools.getFilename(dynamicMeasurement)
        dynamicFilenames.append(reconstructFilenameLabelled)

    # --------------------------CHECKING -----------------------
    # static is only in qtm folder and does not get processed
    runAllQualityProcedures(qtm_folder, [staticFilename])
    runAllQualityProcedures(os.path.join(
        qtm_folder, "processed"), dynamicFilenames)


if __name__ == "__main__":

    main()
