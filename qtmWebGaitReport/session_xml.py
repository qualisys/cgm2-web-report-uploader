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
    result = {
        "Display name": session_xml.find("First_name").text + " " + session_xml.find("Last_name").text,
        "First name": session_xml.find("First_name").text,
        "Last name": session_xml.find("Last_name").text,
        "Patient ID": session_xml.find("Patient_ID").text,
        "Height": session_xml.find("Height").text,
        "Weight": session_xml.find("Weight").text,
        "Diagnosis": session_xml.find("Diagnosis").text,
        "Date of birth": session_xml.find("Date_of_birth").text,
        "Sex": session_xml.find("Sex").text,
        "Test condition": session_xml.find("Test_condition").text,
        "Sub Session Type": session_xml.find("Subsession").get("Type"),
        "Gross Motor Function Classification": session_xml.find("Gross_Motor_Function_Classification").text,
        "Functional Mobility Scale": session_xml.find("Functional_Mobility_Scale").text,
    }
    if session_xml.find("CGM2_Model") is not None:
        result["CGM2 Model"] = session_xml.find("CGM2_Model").text
    return result
