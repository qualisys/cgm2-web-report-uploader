from qtmWebGaitReport.CGM_workflow_main import run_CGM1_workflow_and_return_model
from qtmWebGaitReport.CGM_workflow_main import run_CGM23_workflow_and_return_model
from qtmWebGaitReport.EventDetector_Zeni import prepare_folder_and_run_event_detection
from qtmWebGaitReport.utils import read_session_xml
from qtmWebGaitReport.utils import create_directory_if_needed

import os
import shutil
import glob
import time
import pytest

session_xml_file_name = "session.xml"


@pytest.fixture
def clinical_gait_example_work_folder():
    return os.path.join(
        "TestFiles", "ClinicalGaitExample")


@pytest.fixture
def session_xml(clinical_gait_example_work_folder):
    return read_session_xml(os.path.join(clinical_gait_example_work_folder, session_xml_file_name))


@pytest.fixture
def new_processed_folder_path(clinical_gait_example_work_folder):
    processed_folder_name = "processed_folder_test_generated"
    new_processed_folder_path = os.path.join(
        clinical_gait_example_work_folder, processed_folder_name)
    # copy files to temp folder
    presaved_processed_folder_path = os.path.join(
        clinical_gait_example_work_folder, "processed")
    shutil.copytree(presaved_processed_folder_path,
                    new_processed_folder_path)
    print("SETUP COMPLETE FOR " + str(new_processed_folder_path))
    yield new_processed_folder_path
    print("TEARDOWN")
    shutil.rmtree(new_processed_folder_path)
    print("SUCCESSFUL")


class TestCGM1Workflow:
    def test_runs_without_errors(self, session_xml, new_processed_folder_path):
        # apply workflow
        _ = run_CGM1_workflow_and_return_model(
            session_xml, new_processed_folder_path)
        assert 1, "When this assertion is run all is fine and dandy"


class TestCGM2Workflow:
    def test_runs_without_errors(self, session_xml, new_processed_folder_path):
        model = run_CGM23_workflow_and_return_model(
            session_xml, new_processed_folder_path)
        assert 1, "When this assertion is run all is fine and dandy"


class TestEventDetection:
    def test_zeni_flow(self, session_xml, clinical_gait_example_work_folder):
        processed_folder_name = "with_events_test_generated"

        generated_events_folder = os.path.join(
            clinical_gait_example_work_folder, processed_folder_name)
        # run the detection
        prepare_folder_and_run_event_detection(session_xml,
                                               clinical_gait_example_work_folder, generated_events_folder)
        # compare to presaved c3ds
        processed_to_compare_to = "with_events"
        presaved_events_folder = os.path.join(
            clinical_gait_example_work_folder, processed_to_compare_to)

        for c3d_path in glob.glob(os.path.join(presaved_events_folder, "*.c3d")):
            c3d_name = os.path.split(c3d_path)[-1]
            generated_c3d_path = os.path.join(
                generated_events_folder, c3d_name)
            exists_in_generated = os.path.isfile(generated_c3d_path)
            # the file needs to exist
            assert exists_in_generated, "Did not find %s in %s" % (
                c3d_name, generated_events_folder)
            # and it needs to be the same as before
            with open(c3d_path, "rb") as presaved_c3d:
                with open(generated_c3d_path, "rb") as generated_c3d:
                    assert generated_c3d.read() == presaved_c3d.read(
                    ), "generated event c3d differs from presaved one"
            # cleanup generated file
            os.remove(generated_c3d_path)
