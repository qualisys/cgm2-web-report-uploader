from qtmWebGaitReport.CGM_workflow_main import main as CGM_workflow_main
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--templates-path",
                    default="",
                    help="Give path to Templates directory")
parser.add_argument('--web-report', action='store_true')
parser.add_argument('--pdf-report', action='store_true')
args = parser.parse_args()

if __name__ == "__main__":
    CGM_workflow_main(args)
