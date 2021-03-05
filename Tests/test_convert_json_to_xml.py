import json
import os
from collections import OrderedDict

import pytest
import xmltodict
from qtmWebGaitReport.convert_report_json_to_regression_test_xml import dict_to_xml, get_xml_string_from

report_json_path = os.path.join("TestFiles", "xml_test", "session_data.json")
with open(report_json_path, "r") as f:
    report_json_data = json.load(f)

resave_test_data = False


def load_previous_session_data_xml():
    path_to_previous_session_data = os.path.join("TestFiles", "xml_test", "session_data.xml")
    with open(path_to_previous_session_data, "r") as f:
        previous_report_xml_string = f.read()
    return previous_report_xml_string


@pytest.fixture
def previous_report_xml_string():
    return load_previous_session_data_xml()


def test_check_that_xml_string_has_not_changed(previous_report_xml_string):
    report_xml_string = get_xml_string_from(report_json_data)
    if resave_test_data:
        with open(os.path.join("TestFiles", "xml_test", "session_data.xml"), "w") as f:
            f.write(report_xml_string)
    assert report_xml_string == previous_report_xml_string, "xml string has changed"
