from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from osc_extraction_utils.converter import XlsToCsvConverter
from osc_extraction_utils.exceptions import AnnotationConversionError


@pytest.fixture
def converter() -> XlsToCsvConverter:
    return XlsToCsvConverter(Path("source_folder"), Path("destination_folder"))


def test_convert_method_called(converter) -> None:
    list_paths_sample: list[Path] = [Path()]
    mocked_find_files: Mock = Mock(return_value=list_paths_sample)
    mocked_check_xlsx_files: Mock = Mock()
    mocked_check_valid_paths: Mock = Mock()
    mocked_convert_file: Mock = Mock()

    with (
        patch.object(converter, "_find_xlsx_files_in_source_folder", mocked_find_files),
        patch.object(converter, "_check_xlsx_files", mocked_check_xlsx_files),
        patch.object(converter, "_check_for_valid_paths", mocked_check_valid_paths),
        patch.object(converter, "_convert_single_file_to_csv", mocked_convert_file),
    ):
        converter.convert()

    mocked_find_files.assert_called_once()
    mocked_check_xlsx_files.assert_called_once_with(list_paths_sample)
    mocked_check_valid_paths.assert_called_once()
    mocked_convert_file.assert_called_once_with(list_paths_sample[0])


def test_convert_single_file_to_csv(converter) -> None:
    mocked_read_excel: Mock = Mock()
    path_destination_folder: Path = Path("destination_folder")

    with patch("osc_extraction_utils.converter.pd.read_excel", mocked_read_excel):
        converter._convert_single_file_to_csv(Path("file.xlsx"))

    mocked_read_excel.assert_called_once_with(Path("file.xlsx"), engine="openpyxl")
    path_destination_file: Path = path_destination_folder / "aggregated_annotation.csv"
    mocked_read_excel.return_value.to_csv.assert_called_once_with(
        path_destination_file, index=False, header=True
    )


def test_find_xlsx_files_in_source_folder(converter) -> None:
    mocked_path_glob: Mock = Mock()
    mocked_path_glob.return_value = [Path("file1.xlsx"), Path("file2.xlsx")]

    with patch("osc_extraction_utils.core_utils.Path.glob", mocked_path_glob):
        list_paths_xlsx_files: list[Path] = (
            converter._find_xlsx_files_in_source_folder()
        )

    mocked_path_glob.assert_called_once_with("*.xlsx")
    assert list_paths_xlsx_files == [Path("file1.xlsx"), Path("file2.xlsx")]


def test_check_xlsx_files_single_file(converter) -> None:
    list_paths_xlsx_files: list[Path] = [Path("file.xlsx")]

    try:
        converter._check_xlsx_files(list_paths_xlsx_files)
    except Exception as e:
        pytest.fail(f"An unexpected exception occurred: {e}")


def test_check_xlsx_files_no_files(converter) -> None:
    list_paths_xlsx_files: list = []

    with pytest.raises(AnnotationConversionError):
        converter._check_xlsx_files(list_paths_xlsx_files)


def test_check_xlsx_files_multiple_files(converter) -> None:
    list_paths_xlsx_files: list[Path] = [Path("file1.xlsx"), Path("file2.xlsx")]

    with pytest.raises(AnnotationConversionError):
        converter._check_xlsx_files(list_paths_xlsx_files)


def test_check_for_valid_path_folder_source(converter) -> None:
    converter._path_folder_source = Path()

    with pytest.raises(AnnotationConversionError):
        converter._check_for_valid_paths()


def test_check_for_valid_path_folder_destination(converter) -> None:
    converter._path_folder_destination = Path()

    with pytest.raises(AnnotationConversionError):
        converter._check_for_valid_paths()
