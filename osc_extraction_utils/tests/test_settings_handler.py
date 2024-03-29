from unittest.mock import patch

import pytest

from osc_extraction_utils.conftest import project_tests_root
from osc_extraction_utils.settings_handler import SettingsHandler


@pytest.fixture()
def settings_handler():
    return SettingsHandler()


def test_read_settings_files(settings_handler: SettingsHandler):
    path_tests_root = project_tests_root()
    path_root = path_tests_root.parent.resolve()

    path_settings_main = path_root / "data" / "TEST" / "settings.yaml"
    path_settings_s3 = path_root / "data" / "s3_settings.yaml"

    with patch("osc_extraction_utils.settings_handler.yaml"), patch("builtins.open") as mocked_open:
        settings_handler.read_settings()

        mocked_open.assert_any_call(str(path_settings_main))
        mocked_open.assert_any_call(str(path_settings_s3))


def test_save_settings_file():
    pass


def test_set_settings():
    pass


def test_read_setting_file(settings_handler, path_folder_root_testing):
    path_root = path_folder_root_testing
    path_settings_main = path_root / "data" / "TEST" / "settings.yaml"

    settings_handler._read_setting_file(path_settings_main)
