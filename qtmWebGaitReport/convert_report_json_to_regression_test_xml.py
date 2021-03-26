from collections import defaultdict

import xmltodict


def dict_to_xml(data_dict):
    return xmltodict.unparse(data_dict, pretty=True)


def get_xml_string_from(report_json_data):
    xml_creator = ReportJsonToRegressionXmlCreator()
    xml_creator.prepare_xml_from(report_json_data)
    report_xml_string = xml_creator.get_xml_string()
    return report_xml_string


def save_session_data_xml_from(report_json_data):
    xml_report_string = get_xml_string_from(report_json_data)
    with open("session_data.xml", "w") as f:
        f.write(xml_report_string)


class ReportJsonToRegressionXmlCreator:
    def __init__(self):
        self.dict = {"pyCGM2": {"owner": []}}
        self.xml_to_report_event_mapping = {
            "LHS": "LHS",
            "LMS": "LMS",
            "LOFF": "LOFF",
            "LON": "LON",
            "LTO": "LTO",
            "RANGEEND": "RANGEEND",
            "RANGESTART": "RANGESTART",
            "RHS": "RHS",
            "RMS": "RMS",
            "ROFF": "ROFF",
            "RON": "RON",
            "RTO": "RTO",
            "start": "start",
            "end": "end",
        }
        # all angles, moments, power, GRF, POS?
        self.xml_to_dict_timeseries_with_xyz = {
            "Left Knee Angles": "Left Knee Angles",
            "Left Knee Power": "Left Knee Power",
            "Left Knee Moment": "Left Knee Moment",
            "Left Ankle Angles": "Left Ankle Angles",
            "Left Ankle Moment": "Left Ankle Moment",
            "Left Ankle Power": "Left Ankle Power",
            "Left Hip Angles": "Left Hip Angles",
            "Left Hip Power": "Left Hip Power",
            "Left Hip Moment": "Left Hip Moment",
            "Left Foot Progression": "Left Foot Progression",
            "Left Pelvic Angles": "Left Pelvic Angles",
            "Right Knee Angles": "Right Knee Angles",
            "Right Knee Power": "Right Knee Power",
            "Right Knee Moment": "Right Knee Moment",
            "Right Ankle Angles": "Right Ankle Angles",
            "Right Ankle Moment": "Right Ankle Moment",
            "Right Ankle Power": "Right Ankle Power",
            "Right Hip Angles": "Right Hip Angles",
            "Right Hip Power": "Right Hip Power",
            "Right Hip Moment": "Right Hip Moment",
            "Right Foot Progression": "Right Foot Progression",
            "Right Pelvic Angles": "Right Pelvic Angles",
            "Left Elbow Angles": "Left Elbow Angles",
            "Right Elbow Angles": "Right Elbow Angles",
            "Left Shoulder Angles": "Left Shoulder Angles",
            "Right Shoulder Angles": "Right Shoulder Angles",
            "Left Thorax_Lab Angles": "Left Thorax_Lab Angles",
            "Right Thorax_Lab Angles": "Right Thorax_Lab Angles",
            "Left Thorax Angles": "Left Thorax Angles",
            "Right Thorax Angles": "Right Thorax Angles",
        }
        self.xml_to_dict_metric_MAP = {
            "Left_GPS_ln_mean": "Left_GPS_ln_mean",
            "Overall_GPS_ln_mean": "Overall_GPS_ln_mean",
            "Right_GPS_ln_mean": "Right_GPS_ln_mean",
            "Left Ankle Angles_X_gvs_ln_mean": "Left Ankle Angles_X_gvs_ln_mean",
            "Left Foot Progression_Z_gvs_ln_mean": "Left Foot Progression_Z_gvs_ln_mean",
            "Left Hip Angles_X_gvs_ln_mean": "Left Hip Angles_X_gvs_ln_mean",
            "Left Hip Angles_Y_gvs_ln_mean": "Left Hip Angles_Y_gvs_ln_mean",
            "Left Hip Angles_Z_gvs_ln_mean": "Left Hip Angles_Z_gvs_ln_mean",
            "Left Knee Angles_X_gvs_ln_mean": "Left Knee Angles_X_gvs_ln_mean",
            "Left Pelvic Angles_X_gvs_ln_mean": "Left Pelvic Angles_X_gvs_ln_mean",
            "Left Pelvic Angles_Y_gvs_ln_mean": "Left Pelvic Angles_Y_gvs_ln_mean",
            "Left Pelvic Angles_Z_gvs_ln_mean": "Left Pelvic Angles_Z_gvs_ln_mean",
            "Right Ankle Angles_X_gvs_ln_mean": "Right Ankle Angles_X_gvs_ln_mean",
            "Right Foot Progression_Z_gvs_ln_mean": "Right Foot Progression_Z_gvs_ln_mean",
            "Right Hip Angles_X_gvs_ln_mean": "Right Hip Angles_X_gvs_ln_mean",
            "Right Hip Angles_Y_gvs_ln_mean": "Right Hip Angles_Y_gvs_ln_mean",
            "Right Hip Angles_Z_gvs_ln_mean": "Right Hip Angles_Z_gvs_ln_mean",
            "Right Knee Angles_X_gvs_ln_mean": "Right Knee Angles_X_gvs_ln_mean",
            "Right Pelvic Angles_X_gvs_ln_mean": "Right Pelvic Angles_X_gvs_ln_mean",
            "Right Pelvic Angles_Y_gvs_ln_mean": "Right Pelvic Angles_Y_gvs_ln_mean",
            "Right Pelvic Angles_Z_gvs_ln_mean": "Right Pelvic Angles_Z_gvs_ln_mean",
        }
        self.xml_to_dict_metric_TMPD = {
            "Cadence": "Cadence",
            "Speed": "Speed",
            "Stride_Length": "Stride_Length",
            "Right_Step_Length": "Right_Step_Length",
            "Left_Step_Length": "Left_Step_Length",
            "Stride_Width": "Stride_Width",
            "Right_Stance_Time_Pct": "Right_Stance_Time_Pct",
            "Left_Stance_Time_Pct": "Left_Stance_Time_Pct",
            "Right_Initial_Double_Limb_Support_Time": "Right_Initial_Double_Limb_Support_Time",
            "Left_Initial_Double_Limb_Support_Time": "Left_Initial_Double_Limb_Support_Time",
            "Right_Step_Time": "Right_Step_Time",
            "Left_Step_Time": "Left_Step_Time",
        }

    def prepare_xml_from(self, report_json_data):
        self.report_json_data = report_json_data
        self.prepare_events_data()
        self.prepare_results_data()
        self._add_all_measurements()

    def prepare_events_data(self):
        self.events_for = defaultdict(dict)
        for event_entry in self.report_json_data["events"]:
            for measurement_entry in event_entry["data"]:
                measurement_id = measurement_entry["measurement"]
                self.events_for[measurement_id][event_entry["id"]] = measurement_entry

    def prepare_results_data(self):
        self.results_for = defaultdict(dict)
        for results_entry in self.report_json_data["results"]:
            for measurement_entry in results_entry["data"]:
                measurement_id = measurement_entry["measurement"]
                self.results_for[measurement_id][results_entry["id"]] = measurement_entry

    def _add_all_measurements(self):
        for measurement_dict in self.report_json_data["measurements"]:
            self._add_measurement_data(measurement_dict)

    def _add_measurement_data(self, data_dict):
        cur_id = data_dict["id"]
        self.cur_measurement_data = {"@value": cur_id + ".c3d", "type": []}

        self._add_analog_values(cur_id)

        self._add_event_values(cur_id)

        self._add_timeseries_data(cur_id)

        self._add_metric_data(cur_id)

        self.dict["pyCGM2"]["owner"].append(self.cur_measurement_data)

    def _add_analog_values(self, measurement_id):
        data = {"@value": "ANALOG"}
        data_folder = {"@value": "EMG_RAW_web"}
        # TODO add actual data when I get my hands on an examply with EMG data
        data["folder"] = data_folder
        self.cur_measurement_data["type"].append(data)

    def _add_event_values(self, measurement_id):
        data = {"@value": "EVENT_LABEL"}
        data_folder = self._create_data_folder(self.events_for[measurement_id], self.xml_to_report_event_mapping)
        data["folder"] = data_folder
        self.cur_measurement_data["type"].append(data)

    def _add_timeseries_data(self, measurement_id):
        data_root = {"@value": "LINK_MODEL_BASED"}
        data_folder = self._create_data_folder(
            self.results_for[measurement_id], self.xml_to_dict_timeseries_with_xyz, axis=["X", "Y", "Z"]
        )
        data_root["folder"] = data_folder
        self.cur_measurement_data["type"].append(data_root)

    def _add_metric_data(self, measurement_id):
        root_data = {"@value": "METRIC", "folder": []}
        data_folder = self._create_data_folder(
            self.results_for[measurement_id], self.xml_to_dict_metric_MAP, folder_value="MAP"
        )
        root_data["folder"].append(data_folder)
        data_folder = self._create_data_folder(
            self.results_for[measurement_id], self.xml_to_dict_metric_TMPD, folder_value="TMPD"
        )
        root_data["folder"].append(data_folder)

        self.cur_measurement_data["type"].append(root_data)

    def _create_data_folder(self, measurement_data, mapping, folder_value="ORIGINAL", axis="X"):
        data_folder = {"@value": folder_value, "name": []}
        for xml_label, report_label in mapping.items():
            components = self.get_components(axis, report_label, measurement_data)
            if components != []:
                if len(components) == 1:
                    components = components[0]
                data_folder["name"].append({"@value": xml_label, "component": components})
        return data_folder

    def get_components(self, axis, report_label, measurement_data):
        components = []
        report_label_axis_tuples = self.get_report_label_axis_tuples(axis, report_label)

        for report_label_tuple in report_label_axis_tuples:
            report_label, axis_label = report_label_tuple
            if report_label in measurement_data.keys():
                data = measurement_data[report_label]["values"]
                component = self._create_component(data, axis=axis_label)
                components.append(component)
        return components

    @staticmethod
    def get_report_label_axis_tuples(axis, report_label):
        if type(axis) == list:
            report_label_axis_tuples = [(report_label + "_" + axis_label, axis_label) for axis_label in ["X", "Y", "Z"]]
        else:
            report_label_axis_tuples = [(report_label, "X")]
        return report_label_axis_tuples

    @staticmethod
    def _create_component(data, axis):
        if type(data) == list:
            string_data = ["%.6e" % x for x in data]
        else:
            string_data = ["%.6e" % data]
        component = {"@value": axis, "@frames": len(string_data), "@data": ",".join(string_data)}
        return component

    def get_xml_string(self):
        return dict_to_xml(self.dict)
