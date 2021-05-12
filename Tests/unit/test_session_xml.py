from pathlib import Path

from qtmWebGaitReport.session_xml import create_subject_metadata, load_session_xml_soup

session_xml_file = Path("TestFiles", "GaitWithFunctionalKnee", "session.xml")


class TestParsing:
    def test_parse_subject_metadata(self):
        session_xml = load_session_xml_soup(session_xml_file)
        metadata = create_subject_metadata(session_xml)
        assert len(metadata) >= 13, "Some metadata seems to be missing, length is too short"
