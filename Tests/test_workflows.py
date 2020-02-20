from qtmWebGaitReport.CGM_workflow_main import CGM1_workflow
from qtmWebGaitReport.CGM_workflow_main import CGM23_workflow
from qtmWebGaitReport.utils import read_session_xml

import os
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
        CGM1_workflow(session_xml, clinical_gait_example_work_folder)
        assert 1, "When this assertion is run all is fine and dandy"


def test_CGM2_workflow():
    assert 0
