import os
from distutils.dir_util import copy_tree
from pathlib import Path
import pytest

# from qtmWebGaitReport.CGM_workflow_main import process_and_return_model
from qtmWebGaitReport.CGM_workflow_main import process_with_pycgm, process_with_cgm2
import argparse


@pytest.fixture(
    params=[
        "CGM1.0",
        "CGM1.1",
        "CGM2.1-HJC",
        "CGM2.2-IK",
        "CGM2.3-skinClusters",
        "CGM2.4-ForeFoot",
        "CGM2.5-UpperLimb",
        "CGM2.6-FunctionalKnee",
    ]
)
def model_type(request):
    return request.param


def copy_folder_contents(src_dir, dst_dir):
    copy_tree(src_dir, dst_dir)


new_paf_fields_folder = str(Path("TestFiles", "WithNewPafFields").absolute())
with_functional_knee_folder = str(Path("TestFiles", "GaitWithFunctionalKnee").absolute())


@pytest.mark.slow
@pytest.mark.parametrize(
    "model_type",
    [
        "CGM1.0",
        "CGM1.1",
        "CGM2.1-HJC",
        "CGM2.2-IK",
        "CGM2.3-skinClusters",
        "CGM2.4-ForeFoot",
    ],
)
def test_up_to_24(model_type, tmp_path):
    copy_folder_contents(new_paf_fields_folder, str(tmp_path))
    if Path.cwd() != tmp_path:
        os.chdir(str(tmp_path))
    # try:
    args = argparse.Namespace(debug=False, sessionFile="session.xml")
    process_with_cgm2(args, model_type, generate_pdf_report=False, check_events_in_mokka=False)
    # except Exception as e:
    #     assert 0, "Unexpected error: {}".format(e)


@pytest.mark.parametrize(
    "model_type",
    [
        "CGM2.5-UpperLimb",
        "CGM2.6-FunctionalKnee",
    ],
)
def test_from_25(model_type, tmp_path):
    copy_folder_contents(with_functional_knee_folder, str(tmp_path))
    if Path.cwd() != tmp_path:
        os.chdir(str(tmp_path))
    # try:
    args = argparse.Namespace(debug=False, sessionFile="session.xml")
    process_with_cgm2(args, model_type, generate_pdf_report=False, check_events_in_mokka=False)
    # except Exception as e:
    #     assert 0, "Unexpected error: {}".format(e)
