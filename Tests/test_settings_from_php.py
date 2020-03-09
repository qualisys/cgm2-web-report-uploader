from qtmWebGaitReport.pyCGM_workflows.reporting import load_settings_from_php
from pathlib2 import Path

path_to_settings_php = Path("TestFiles") / "settings.php"


def test_load_settings():
    settings_dict = load_settings_from_php(str(path_to_settings_php))
    key_value_pairs_to_check = {"force_threshold": 10}
    for key_to_check, value_to_check in key_value_pairs_to_check.items():
        assert key_to_check in settings_dict.keys(
        ), "{} not in settings_dict.keys(): {}".format(key_to_check, settings_dict.keys())
        assert settings_dict[key_to_check] == value_to_check, "value for {} is wrong: {} != {}".format(
            key_to_check, settings_dict[key_to_check], value_to_check)
