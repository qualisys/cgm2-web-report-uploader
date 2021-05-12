from pathlib import Path

from qtmWebGaitReport.session_xml import (
    create_measurement_metadata,
    create_subject_metadata,
    get_update_existing_report,
    load_session_xml_soup,
)

session_xml_file = Path("TestFiles", "GaitWithFunctionalKnee", "session.xml")


class TestParsing:
    def test_parse_subject_metadata(self):
        session_xml = load_session_xml_soup(session_xml_file)
        metadata = create_subject_metadata(session_xml)
        assert len(metadata) >= 13, "Some metadata seems to be missing, length is too short"

    def test_parse_measurement_metadata(self):
        session_xml = load_session_xml_soup(session_xml_file)
        metadata = create_measurement_metadata(session_xml, measurement_name="Gait FB - CGM2 2")
        assert len(metadata) >= 21, "Some metadata seems to be missing, length is too short"

    def test_update_existing_report(self):
        session_xml = load_session_xml_soup(session_xml_file)
        update_existing_report = get_update_existing_report(session_xml)
        assert update_existing_report == True, "Should be True but was False"
