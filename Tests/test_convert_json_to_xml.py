from qtmWebGaitReport.convert_report_json_to_regression_test_xml import get_xml_string_from
from qtmWebGaitReport.convert_report_json_to_regression_test_xml import dict_to_xml
import os
import json
import xmltodict
import pytest

report_json_path = os.path.join(
    "TestFiles", "xml_test", "session_data.json")
with open(report_json_path, "r") as f:
    report_json_data = json.load(f)


def load_previous_session_data_xml():
    path_to_previous_session_data = os.path.join(
        "TestFiles", "xml_test", "session_data.xml")
    with open(path_to_previous_session_data, "r") as f:
        previous_report_xml_string = f.read()
    return previous_report_xml_string


@pytest.fixture
def previous_report_xml_string():
    return load_previous_session_data_xml()


def test_check_that_xml_string_has_not_changed(previous_report_xml_string):
    report_xml_string = get_xml_string_from(report_json_data)
    assert report_xml_string == previous_report_xml_string, "xml string has changed"
