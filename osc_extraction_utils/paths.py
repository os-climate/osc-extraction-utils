from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

from osc_extraction_utils.helpers import create_tmp_file_path
from osc_extraction_utils.settings import MainSettings

path_file_running = create_tmp_file_path()

# TODO some legacy code, required or not?
# try:
#     path = globals()['_dh'][0]
# except KeyError:
#     path = os.path.dirname(os.path.realpath(__file__))


class ProjectPaths(BaseSettings):
    _PATH_FOLDER_ROOT: Path = Path()
    _PATH_FOLDER_NLP: Path = _PATH_FOLDER_ROOT
    _PATH_FOLDER_MODEL: Path = _PATH_FOLDER_ROOT / "models"
    _PATH_FOLDER_DATA: Path = _PATH_FOLDER_ROOT / "data"
    # TODO move somewhere else since it is no path...
    _PYTHON_EXECUTABLE: str = "python"

    _string_project_name: str
    _path_project_data_folder: Path
    _path_project_model_folder: Path
    _main_settings: MainSettings

    path_folder_source_pdf: Path = Field(default=Path("input/pdfs/training"))
    path_folder_source_annotation: Path = Field(default=Path("input/annotations"))
    path_folder_source_mapping: Path = Field(default=Path("input/kpi_mapping"))
    path_folder_destination_pdf: Path = Field(default=Path("interim/pdfs"))
    path_folder_destination_annotation: Path = Field(default=Path("interim/ml/annotations"))
    path_folder_destination_mapping: Path = Field(default=Path("interim/kpi_mapping"))
    path_folder_destination_extraction: Path = Field(default=Path("interim/ml/extraction"))
    path_folder_destination_curation: Path = Field(default=Path("interim/ml/curation"))
    path_folder_destination_training: Path = Field(default=Path("interim/ml/training"))

    path_folder_destination_saved_models_relevance: Path = Field(default=Path("RELEVANCE/Text"))
    path_folder_destination_saved_models_inference: Path = Field(default=Path("KPI_EXTRACTION/Text"))

    path_folder_text_3434: Path = Field(default=Path("interim/ml"))
    path_folder_relevance: Path = Field(default=Path("output/RELEVANCE/Text"))

    def __init__(self, string_project_name: str, main_settings: MainSettings, path_folder_root: Path, **kwargs):
        super().__init__(**kwargs)
        if not isinstance(string_project_name, str):
            raise TypeError
        self._string_project_name: str = string_project_name
        self._PATH_FOLDER_ROOT = path_folder_root.resolve()
        self._path_project_data_folder: Path = self._PATH_FOLDER_DATA / Path(string_project_name)
        self._path_project_model_folder: Path = self._PATH_FOLDER_MODEL / Path(string_project_name)
        self._main_settings: MainSettings = main_settings
        self._update_all_paths_depending_on_path_project_data_folder()
        self._update_all_paths_depending_on_path_project_model_folder()
        self._update_all_root_related_paths()
        self._create_all_root_related_folders()

    @property
    def string_project_name(self) -> str:
        return self._string_project_name

    @string_project_name.setter
    def string_project_name(self, string_new_project_name: str) -> None:
        if not isinstance(string_new_project_name, str):
            raise TypeError

        self._string_project_name: str = string_new_project_name
        self._update_all_paths_depending_on_path_project_data_folder()
        self._update_all_paths_depending_on_path_project_model_folder()

    @property
    def path_project_data_folder(self) -> Path:
        return self._path_project_data_folder

    @property
    def path_project_model_folder(self) -> Path:
        return self._path_project_model_folder

    @property
    def main_settings(self) -> MainSettings:
        return self._main_settings

    @main_settings.setter
    def main_settings(self, main_settings_new: MainSettings) -> None:
        self._main_settings: MainSettings = main_settings_new
        self._update_all_paths_depending_on_path_project_model_folder()

    @property
    def PATH_FOLDER_ROOT(self) -> Path:
        return self._PATH_FOLDER_ROOT

    @PATH_FOLDER_ROOT.setter
    def PATH_FOLDER_ROOT(self, path_folder_root_new: Path) -> None:
        if not isinstance(path_folder_root_new, Path):
            raise TypeError
        self._PATH_FOLDER_ROOT = path_folder_root_new
        self._update_all_root_related_paths()
        self._create_all_root_related_folders()

    @property
    def PATH_FOLDER_NLP(self) -> Path:
        return self._PATH_FOLDER_NLP

    @property
    def PATH_FOLDER_MODEL(self) -> Path:
        return self._PATH_FOLDER_MODEL

    @property
    def PATH_FOLDER_DATA(self) -> Path:
        return self._PATH_FOLDER_DATA

    @property
    def PYTHON_EXECUTABLE(self) -> str:
        return self._PYTHON_EXECUTABLE

    def _update_all_paths_depending_on_path_project_data_folder(self) -> None:
        list_paths_model_fields_filtered: list[str] = [
            path_model_field for path_model_field in self.model_fields.keys() if "saved_models" not in path_model_field
        ]

        for path_field in list_paths_model_fields_filtered:
            path_field_default: Path = self.model_fields[path_field].default
            setattr(
                self, f"{path_field}", self._PATH_FOLDER_DATA / Path(self._string_project_name) / path_field_default
            )

    def _update_all_root_related_paths(self) -> None:
        self._PATH_FOLDER_NLP: Path = self.PATH_FOLDER_ROOT
        self._PATH_FOLDER_MODEL: Path = self.PATH_FOLDER_ROOT / "models"
        self._PATH_FOLDER_DATA: Path = self.PATH_FOLDER_ROOT / "data"

    def _create_all_root_related_folders(self) -> None:
        self._PATH_FOLDER_MODEL.mkdir(parents=True, exist_ok=True)  # includes root folder
        self._PATH_FOLDER_DATA.mkdir(exist_ok=True)

    def _update_all_paths_depending_on_path_project_model_folder(self) -> None:
        list_string_paths_depending_on_path_project_model_folder: list[str] = [
            "path_folder_destination_saved_models_relevance",
            "path_folder_destination_saved_models_inference",
        ]
        list_paths_main_settings: list[Path] = [
            Path(self._main_settings.train_relevance.output_model_name),
            Path(self._main_settings.train_kpi.output_model_name),
        ]

        for string_model_field, path_main_settings in zip(
            list_string_paths_depending_on_path_project_model_folder, list_paths_main_settings
        ):
            setattr(
                self,
                string_model_field,
                self._PATH_FOLDER_MODEL
                / Path(self._string_project_name)
                / self.model_fields[string_model_field].default
                / path_main_settings,
            )


# TODO implement setup for global use in project
_current_project_paths: ProjectPaths | None = None


def get_project_settings() -> ProjectPaths:
    if _current_project_paths is None:
        raise TypeError
    return _current_project_paths
