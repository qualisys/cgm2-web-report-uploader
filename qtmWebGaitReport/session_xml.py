from pathlib import Path
from typing import Dict, Union

from bs4 import BeautifulSoup

SESSION_XML_FILENAME = "session.xml"


def load_session_xml_soup(path: Union[Path, str]) -> BeautifulSoup:
    path = Path(path)
    with path.open("rb") as f:
        content = f.read()

    result = BeautifulSoup(content, "xml")
    return result


def create_subject_metadata(session_xml: BeautifulSoup) -> Dict:
    session_fields = {x.name.replace("_", " "): x.text for x in session_xml.find("Session").find("Fields").find_all()}
    sub_session_fields = {
        x.name.replace("_", " "): x.text for x in session_xml.find("Subsession").find("Fields").find_all()
    }
    subject_fields = {x.name.replace("_", " "): x.text for x in session_xml.find("Subject").find("Fields").find_all()}
    result = {**session_fields, **sub_session_fields, **subject_fields}
    result["Sub Session Type"] = session_xml.find("Subsession").get("Type")
    return result


def create_measurement_metadata(session_xml: BeautifulSoup, measurement_name: str) -> Dict:
    measurement_entry = [x for x in session_xml.find_all("Measurement") if measurement_name in x.get("Filename")][0]
    result = {x.name.replace("_", " "): x.text for x in measurement_entry.find("Fields").find_all()}
    return result
