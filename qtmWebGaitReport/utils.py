from bs4 import BeautifulSoup
from datetime import datetime

import logging
import os


def read_session_xml(path):
    with open(path, "r") as f:
        contents = f.read()
        soup = BeautifulSoup(contents, 'xml')
    return soup


def get_creation_date(session_xml):
    date_str = session_xml.Subject.Session.Creation_date.text
    year, month, day = date_str.split("-")
    time_str = session_xml.Subject.Session.Creation_time.text
    hour, minute, second = time_str.split(":")
    datetime_obj = datetime(
        int(year), int(month), int(day),
        int(hour), int(minute), int(second))
    return datetime_obj


def create_directory_if_needed(path):
    if not os.path.isdir(path):
        os.makedirs(path)
    else:
        logging.warning("directory already exists")
