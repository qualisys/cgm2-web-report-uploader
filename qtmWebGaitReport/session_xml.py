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

    for key_to_remove in ["Directory pattern", "Measurement pattern"]:
        result.pop(key_to_remove, None)
    return result


def create_measurement_metadata(session_xml: BeautifulSoup, measurement_name: str) -> Dict:
    measurement_entries = [x for x in session_xml.find_all("Measurement") if measurement_name in x.get("Filename")]
    if len(measurement_entries) == 0:
        return {}
    measurement_entry = measurement_entries[0]
    result = {x.name.replace("_", " "): x.text for x in measurement_entry.find("Fields").find_all()}

    for key_to_remove in ["Directory pattern", "Measurement pattern"]:
        result.pop(key_to_remove, None)
    return result


def get_update_existing_report(session_xml: BeautifulSoup) -> bool:
    result_str = session_xml.find("Update_existing_web_report").text
    result = True if result_str == "True" else False
    return result
