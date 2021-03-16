import argparse
import os

from qtmWebGaitReport.CGM_workflow_main import main as CGM_workflow_main

parser = argparse.ArgumentParser()
parser.add_argument("--templates-path", default="", help="Give path to Templates directory")
parser.add_argument("--web-report", action="store_true")
parser.add_argument("--pdf-report", action="store_true")
parser.add_argument("--change-cwd", default="")
args = parser.parse_args()

if __name__ == "__main__":
    if args.change_cwd != "":

        os.chdir(args.change_cwd)
    CGM_workflow_main(args)
