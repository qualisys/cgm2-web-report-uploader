from qtmWebGaitReport.measurements import Measurements
from pathlib2 import Path

working_directory = Path("TestFiles","ForMeasurementSectionTest","processed")

def test_that_each_measurement_has_exactly_2_video_resources():
    meas = Measurements(str(working_directory))
    measurement_info = meas.measurementInfo()
    for info in measurement_info:
        video_resources = []
        for resource in info["resources"]:
            if resource["type"] == "video":
                video_resources.append(resource)
        assert len(video_resources) == 2, "num_video_resources {} != 2".format(len(video_resources))
        