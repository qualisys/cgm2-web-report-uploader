from qtmWebGaitReport.CGM_workflow_main import main as CGM_workflow_main
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--settings-php-path",
                    default="",
                    help="Give path to settings.php file to load some settings from the file")
args = parser.parse_args()

if __name__ == "__main__":
    CGM_workflow_main(args)
