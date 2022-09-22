from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

from clearml import Dataset

from .connector import DatasetConnector


class ClearMLDataset(DatasetConnector):
    def __init__(self):
        super().__init__()
        # Add type hinting for dataset
        self.dataset: Optional[Dataset] = None

    @property
    def file_entries(self) -> Dict:
        if self.dataset is None:
            raise AttributeError("Dataset has not been initialized")
        return self.dataset.file_entries_dict

    @classmethod
    def get(
        cls,
        id: Optional[str] = None,
        project: Optional[str] = None,
        name: Optional[str] = None,
        version: Optional[str] = None,
    ) -> "ClearMLDataset":
        dataset = cls()
        dataset.dataset = Dataset.get(
            dataset_id=id,
            dataset_name=name,
            dataset_project=project,
            dataset_version=version,
        )
        dataset.id = dataset.dataset.id
        dataset.default_remote = dataset.dataset.get_default_storage()
        return dataset

    @classmethod
    def create(
        cls,
        name: Optional[str] = None,
        version: Optional[str] = None,
        project: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
        default_remote: Optional[str] = None,
        description: Optional[str] = None,
    ) -> "ClearMLDataset":
        dataset = cls()
        dataset.dataset = Dataset.create(
            dataset_name=name,
            dataset_project=project,
            dataset_tags=tags,
            dataset_version=version,
            output_uri=default_remote,
            description=description,
        )
        dataset.id = dataset.dataset.id
        dataset.default_remote = default_remote
        return dataset

    @staticmethod
    def list_datasets(
        project: Optional[str] = None,
        partial_name: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
        ids: Optional[Sequence[str]] = None,
    ) -> List[Dict]:
        return Dataset.list_datasets(
            partial_name=partial_name, dataset_project=project, ids=ids, tags=tags
        )

    def add_files(self, path: Union[str, Path], recursive: bool = True) -> None:
        if self.dataset is None:
            raise AttributeError("Dataset has not been created.")
        self.dataset.add_files(path=path, recursive=recursive)

    def remove_files(self, path: Union[str, Path], recursive: bool = True) -> None:
        if self.dataset is None:
            raise AttributeError("Dataset has not been created.")
        self.dataset.remove_files(path=path, recursive=recursive)

    def upload(self, remote: Optional[str] = None) -> None:
        if self.dataset is None:
            raise AttributeError("Dataset has not been created.")
        if remote is None:
            if self.default_remote is None:
                raise ValueError("No output value specified")
            else:
                self.logger.warning(
                    f"No remote url specified, using default remote of {self.default_remote}"
                )
                remote = self.default_remote
        self.dataset.upload(output_url=remote)
        # NOTE: no idea if the below one is necessary
        self.dataset.finalize()

    def download(self, path: Union[str, Path], overwrite: bool = True) -> str:
        if self.dataset is None:
            raise AttributeError("Dataset has not been created.")
        self.output_path = self.dataset.get_mutable_local_copy(
            target_folder=path, overwrite=overwrite
        )
        return self.output_path

    def delete(self) -> None:
        # If dataset does not exist, then
        # no need to do anything
        if self.dataset is not None:
            self.dataset.delete()
