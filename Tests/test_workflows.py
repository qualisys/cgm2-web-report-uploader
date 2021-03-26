import os
from distutils.dir_util import copy_tree
from pathlib import Path

import pytest
from qtmWebGaitReport.CGM_workflow_main import process_and_return_model


@pytest.fixture(params=["CGM1.0", "CGM1.1", "CGM2.1-HJC", "CGM2.2-IK", "CGM2.3-skinClusters", "CGM2.4-ForeFoot"])
def model_type(request):
    return request.param


def copy_folder_contents(src_dir, dst_dir):
    copy_tree(src_dir, dst_dir)


new_paf_fields_folder = str(Path("TestFiles", "WithNewPafFields").absolute())


@pytest.mark.slow
def test_new_paf_fields(model_type, tmp_path):
    copy_folder_contents(new_paf_fields_folder, str(tmp_path))
    if Path.cwd() != tmp_path:
        os.chdir(str(tmp_path))
    try:
        process_and_return_model(model_type, check_events_in_mokka=False)
    except Exception as e:
        assert 0, "Unexpected error: {}".format(e)
