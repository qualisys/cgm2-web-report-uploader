import os
from pyCGM2.Utils import files
from qtmWebGaitReport.CGM1_workflow import main as CGM1_workflow_main


def main():
    file = "session.xml"
    sessionXML = files.readXml(os.getcwd()+"\\", file)
    pyCGM_processing_type = sessionXML.Subsession.pyCGM_Processing_Type.text

    if pyCGM_processing_type == "pyCGM1":
        CGM1_workflow_main(sessionXML)
    else:
        raise Exception(
            "Only pyCGM1 processing is currently implemented, but you selected %s" % pyCGM_processing_type)
