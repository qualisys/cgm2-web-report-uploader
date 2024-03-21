import os
from distutils.dir_util import copy_tree
from shutil import copyfile
from pathlib import Path
import pytest

from qtmWebGaitReport.CGM_workflow_main import process_with_cgm2
import argparse


def copy_folder_contents(src_dir, dst_dir):
    copy_tree(src_dir, dst_dir)


new_paf_fields_folder = str(Path("TestFiles", "WithNewPafFields").absolute())
with_functional_knee_folder = str(Path("TestFiles", "GaitWithFunctionalKnee").absolute())
session_xml_files = {
    "CGM1.0": str(Path("TestFiles", "WithNewPafFields", "session_cgm10.xml").absolute()),
    "CGM1.1": str(Path("TestFiles", "WithNewPafFields", "session_cgm11.xml").absolute()),
    "CGM2.1-HJC": str(Path("TestFiles", "WithNewPafFields", "session_cgm21.xml").absolute()),
    "CGM2.2-IK": str(Path("TestFiles", "WithNewPafFields", "session_cgm22.xml").absolute()),
    "CGM2.3-skinClusters": str(Path("TestFiles", "WithNewPafFields", "session_cgm23.xml").absolute()),
    "CGM2.4-ForeFoot": str(Path("TestFiles", "WithNewPafFields", "session_cgm24.xml").absolute()),
    "CGM2.5-UpperLimb": str(Path("TestFiles", "GaitWithFunctionalKnee", "session_cgm25.xml").absolute()),
    "CGM2.6-FunctionalKnee": str(Path("TestFiles", "GaitWithFunctionalKnee", "session_cgm26.xml").absolute()),
}


def copy_correct_session_xml(model_type, tmp_path):
    session_xml = session_xml_files[model_type]
    # copy session xml file as session.xml, remove existing one from tmp_path
    # remove session.xml from tmp_path
    if Path(tmp_path / "session.xml").exists():
        os.remove(tmp_path / "session.xml")
    copyfile(session_xml, tmp_path / "session.xml")


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
    copy_correct_session_xml(model_type, tmp_path)

    if Path.cwd() != tmp_path:
        os.chdir(str(tmp_path))
    try:
        args = argparse.Namespace(debug=False, sessionFile="session.xml")
        process_with_cgm2(args)
    except Exception as e:
        assert 0, "Unexpected error: {}".format(e)


@pytest.mark.parametrize(
    "model_type",
    [
        "CGM2.5-UpperLimb",
        "CGM2.6-FunctionalKnee",
    ],
)
def test_from_25(model_type, tmp_path):
    copy_folder_contents(with_functional_knee_folder, str(tmp_path))
    copy_correct_session_xml(model_type, tmp_path)
    if Path.cwd() != tmp_path:
        os.chdir(str(tmp_path))
    try:
        args = argparse.Namespace(debug=False, sessionFile="session.xml")
        process_with_cgm2(args)
    except Exception as e:
        assert 0, "Unexpected error: {}".format(e)
