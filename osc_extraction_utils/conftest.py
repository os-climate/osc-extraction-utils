import os
import shutil
import sys
import typing
from pathlib import Path
from typing import Generator
from unittest.mock import patch

import pandas as pd
import pytest

from osc_extraction_utils.paths import ProjectPaths
from osc_extraction_utils.settings import (
    MainSettings,
    S3Settings,
    get_main_settings,
    get_s3_settings,
)

# add test_on_pdf.py to the PATH
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def project_tests_root() -> Path:
    """returns the absolute project root path

    :return: Path to the current project root
    :rtype: Path
    """
    return Path(__file__).parent.resolve()


def write_to_file(path_csv_file: Path, content: str, header: str = ""):
    """Write to a file for a given path with an optional header string

    :param path_csv_file: Path to csv file
    :type path_csv_file: Path
    :param content: Content which should be written to csv file
    :type content: str
    :param header: Header of the csv file, defaults to ''
    :type header: str, optional
    """
    with open(str(path_csv_file), "w") as file:
        if len(header) > 0:
            file.write(f"{header}\n")
        file.write(f"{content}\n")


def create_single_xlsx_file(path_folder: Path, file_name="xlsx_file.xlsx") -> None:
    """Writes a single xlsx file to path_folder and creates the folder if it does not
    exist

    :param path_folder: Path to folder where the single xlsx file should be created
    :type path_folder: Path
    :param file_name: Filename of the xlsx file, defaults to 'xlsx_file.xlsx'
    :type file_name: str, optional
    """
    path_folder.mkdir(parents=True, exist_ok=True)

    # write single xlsx file
    df_current = pd.DataFrame({"Data": [10, 20, 30, 40, 50, 60]})
    path_current_file = path_folder / file_name
    df_current.to_excel(str(path_current_file), engine="openpyxl")


def create_multiple_xlsx_files(path_folder: Path) -> None:
    """Writes multiple xlsx file to path_folder and creates the folder if it does not
    exist

    :param path_folder: Path to folder where the single xlsx file should be created
    :type path_folder: Path
    """
    for i in range(5):
        create_single_xlsx_file(path_folder, file_name=f"xlsx_file_{i}.xlsx")


def modify_project_settings(project_settings: typing.Dict, *args: typing.Tuple[str, str, bool]) -> typing.Dict:
    """Returns are modified project settings dict based on the input args

    :param project_settings: Project settings
    :type project_settings: typing.Dict
    :return: Modified project settings
    :rtype: typing.Dict
    """
    for modifier in args:
        # check for valid args
        if len(modifier) == 3:
            key1, key2, decision = modifier
            project_settings[key1][key2] = decision
    return project_settings


@pytest.fixture(scope="session")
def path_folder_temporary() -> Generator:
    """Fixture for defining path for running check

    :return: Path to the temporary folder
    :rtype: Path
    :yield: Path to the temporary folder
    :rtype: Iterator[Path]
    """
    path_folder_temporary_ = project_tests_root() / "temporary_folder"
    # delete the temporary folder and recreate it
    shutil.rmtree(path_folder_temporary_, ignore_errors=True)
    path_folder_temporary_.mkdir()
    yield path_folder_temporary_

    # cleanup
    shutil.rmtree(path_folder_temporary_, ignore_errors=True)


@pytest.fixture(scope="session")
def path_folder_root_testing() -> Generator:
    path_folder_data_sample_ = project_tests_root() / "tests" / "root_testing"
    yield path_folder_data_sample_


@pytest.fixture(scope="session")
def main_settings() -> MainSettings:
    return get_main_settings()


@pytest.fixture(scope="session")
def s3_settings() -> S3Settings:
    return get_s3_settings()


# TODO add test mode paths?
@pytest.fixture(scope="session")
def project_paths(main_settings: MainSettings) -> ProjectPaths:
    return ProjectPaths("test_project", main_settings, Path(__file__).parents[1].resolve())


@pytest.fixture(scope="session")
def prerequisites_generate_text(
    path_folder_temporary: Path, project_paths: ProjectPaths
) -> Generator[None, None, None]:
    """Defines a fixture for mocking all required paths and creating required temporary folders

    :param path_folder_temporary: Requesting the path_folder_temporary fixture
    :type path_folder_temporary: Path
    :rtype: None
    """
    path_folder_relevance = path_folder_temporary / "relevance"
    path_folder_text_3434 = path_folder_temporary / "folder_test_3434"
    path_folder_relevance.mkdir(parents=True)
    path_folder_text_3434.mkdir(parents=True)
    project_paths.path_folder_relevance = path_folder_temporary / "relevance"
    project_paths.path_folder_text_3434 = path_folder_text_3434

    # create multiple files in the folder_relevance with the same header
    for i in range(5):
        path_current_file = path_folder_relevance / f"{i}_test.csv"
        path_current_file.touch()
        write_to_file(path_current_file, f"That is a test {i}", "HEADER")

    with (
        patch.object(project_paths, "path_folder_relevance", Path(path_folder_relevance)),
        patch.object(project_paths, "path_folder_text_3434", Path(path_folder_text_3434)),
        patch("osc_extraction_utils.merger.os.getenv", lambda *args: args[0]),
    ):
        yield

    # cleanup
    for path in path_folder_temporary.glob("*"):
        shutil.rmtree(path)
