from qtmWebGaitReport.CGM_workflow_main import main as CGM_workflow_main
from qtmWebGaitReport.EventDetector_Zeni import main as EventDetector_Zeni_main
from qtmWebGaitReport.pyCGM2_dataQuality import main as dataQuality_main

if __name__ == "__main__":
    EventDetector_Zeni_main()
    dataQuality_main()
    CGM_workflow_main()
