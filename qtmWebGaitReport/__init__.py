import sys
import os

GAIT_WEB_REPORT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

# determine if application is a script file or frozen exe
if getattr(sys, "frozen", False):
    PATH_TO_MAIN = os.path.dirname(sys.executable)
elif __file__:
    PATH_TO_MAIN = GAIT_WEB_REPORT_PATH
