from qtmWebGaitReport.CGM_workflow_main import CGM1_workflow
from qtmWebGaitReport.CGM_workflow_main import CGM23_workflow
from qtmWebGaitReport.EventDetector_Zeni import run_event_detection_and_verify_in_mokka
from qtmWebGaitReport.utils import read_session_xml
from qtmWebGaitReport.utils import create_directory_if_needed

import os
import shutil
import glob
import pytest

session_xml_file_name = "session.xml"


@pytest.fixture
def clinical_gait_example_work_folder():
    return os.path.join(
        "TestFiles", "ClinicalGaitExample")


@pytest.fixture
def session_xml(clinical_gait_example_work_folder):
    return read_session_xml(os.path.join(clinical_gait_example_work_folder, session_xml_file_name))


class TestCGM1Workflow:
    def test_runs_without_errors(self, session_xml, clinical_gait_example_work_folder):
        # create a copy of processed files folder
        processed_folder_name = "processed_folder_test_generated"
        new_processed_folder_path = os.path.join(
            clinical_gait_example_work_folder, processed_folder_name)
        presaved_processed_folder_path = os.path.join(
            clinical_gait_example_work_folder, "processed")
        shutil.copytree(presaved_processed_folder_path,
                        new_processed_folder_path)
        # apply workflow
        CGM1_workflow(session_xml, clinical_gait_example_work_folder,
                      processed_folder_name=processed_folder_name)
        assert 1, "When this assertion is run all is fine and dandy"
        # cleanup
        shutil.rmtree(new_processed_folder_path)


class TestEventDetection:
    def test_zeni_flow(self, clinical_gait_example_work_folder):
        processed_folder_name = "with_events_test_generated"
        processed_to_compare_to = "with_events"
        # run the detection
        run_event_detection_and_verify_in_mokka(
            clinical_gait_example_work_folder, processed_folder_name)
        # compare to presaved c3ds
        presaved_events_folder = os.path.join(
            clinical_gait_example_work_folder, processed_to_compare_to)
        generated_events_folder = os.path.join(
            clinical_gait_example_work_folder, processed_folder_name)
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

# def test_CGM2_workflow():
#     assert 0
