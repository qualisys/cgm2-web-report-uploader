# -*- coding: utf-8 -*-

from qtmWebGaitReport import qtools
import os
from pathlib import Path
import json
from datetime import datetime
from qtmWebGaitReport import c3dValidation


def get_creation_date(file):
    stat = os.stat(file)
    try:
        return stat.st_birthtime
    except AttributeError:
        return stat.st_mtime


def create_resources(video_filenames, extra_settings):

    if "Cameras" in extra_settings.keys():
        all_video_serials = list(extra_settings["Cameras"].keys())
    else:
        all_video_serials = []
    resources = []
    for video_filename in video_filenames:
        video_name = video_filename.replace(".mp4", "")
        cur_resource = {
            "type": "video",
            "name": video_name,
            "src": video_filename,
        }
        current_serial = [serial for serial in all_video_serials if str(serial) in video_name]
        if current_serial != []:
            current_serial = current_serial[0]
            if "Group" in extra_settings["Cameras"][current_serial].keys():
                cur_resource["group"] = extra_settings["Cameras"][current_serial]["Group"]
        resources.append(cur_resource)
    return resources


def get_current_measurement_mp4(measurement_name, video_meta):
    # type: (List) -> List
    measurement_videos = []
    for cur_video in video_meta:
        measurement_for_cur_video = str(Path(cur_video["measurement"]).stem)
        if measurement_name == measurement_for_cur_video:
            measurement_videos.append(Path(cur_video["outputPath"]).name)
    return measurement_videos


def load_videos_json(session_folder):
    # type: (Path) -> List
    video_json_path = session_folder / "videos.json"
    if video_json_path.is_file():
        with video_json_path.open("r") as f:
            video_meta = json.load(f)
    else:
        video_meta = []
    return video_meta


class Measurements:
    def __init__(self, workingDirectory):
        self.workingDirectory = workingDirectory

        c3dValObj = c3dValidation.c3dValidation(workingDirectory)
        self.fileNames = c3dValObj.getValidC3dList(False)

    def measurementInfo(self, extra_settings={}):
        info = []
        session_folder = Path(self.workingDirectory).absolute().parent
        video_meta = load_videos_json(session_folder)
        for filename in self.fileNames:
            acq = qtools.fileOpen(filename)
            measurementName = Path(filename).stem

            val = acq.GetDuration()
            startOffset = acq.GetFirstFrame() / acq.GetPointFrequency()
            frameRate = acq.GetPointFrequency()
            originalDuration = acq.GetDuration()
            creation_date = datetime.fromtimestamp(get_creation_date(filename))
            creationDate = str(creation_date.date())
            creationTime = str(creation_date.time())

            diagnosis = ""

            patientName = "UNSPECIFIED"
            bodyHeight = 0
            bodyWeight = 0

            video_filenames = get_current_measurement_mp4(measurementName, video_meta)
            resources = create_resources(video_filenames, extra_settings)

            fields = [
                {"id": "Creation date", "value": creationDate, "type": "text"},
                {"id": "Creation time", "value": creationTime, "type": "text"},
                {"id": "Diagnosis", "value": diagnosis, "type": "text"},
                {"id": "Last name", "value": patientName, "type": "text"},
                {"id": "Height", "value": bodyHeight, "type": "text"},
                {"id": "Weight", "value": bodyWeight, "type": "text"},
            ]

            info.append(
                {
                    "duration": val,
                    "startOffset": startOffset,
                    "originalDuration": originalDuration,
                    "rate": frameRate,
                    "id": measurementName,
                    "fields": fields,
                    "resources": resources,
                }
            )
        return info
