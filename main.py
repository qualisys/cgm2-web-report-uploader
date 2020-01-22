from qtmWebGaitReport.CGM1_workflow import main as CGM1_workflow_main
from qtmWebGaitReport.EventDetector_Zeni import main as EventDetector_Zeni_main
from qtmWebGaitReport.pyCGM2_dataQuality import main as dataQuality_main

if __name__ == "__main__":
    EventDetector_Zeni_main()
    dataQuality_main()
    CGM1_workflow_main()
