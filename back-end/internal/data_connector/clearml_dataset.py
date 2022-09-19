from pathlib import Path
from typing import Optional, Sequence, Union
from clearml import Dataset
from connector import DatasetConnector


class ClearMLDataset(DatasetConnector):
    @property
    def id(self):
        try:
            return self.dataset.id
        except AttributeError:
            raise AttributeError("Dataset has not been created or initialized.")

    @property
    def file_entries_dict(self):
        try:
            return self.dataset.file_entries_dict()
        except AttributeError:
            raise AttributeError("Dataset has not been created or initialized.")

    @classmethod
    def from_id(cls, id: str):
        dataset = cls()
        dataset.dataset = Dataset.get(id)
        return dataset

    @classmethod
    def from_scratch(
        cls,
        dataset_name: Optional[str] = None,
        dataset_project: Optional[str] = None,
        dataset_tags: Optional[Sequence[str]] = None,
        dataset_version: Optional[str] = None,
        output_uri: Optional[str] = None,
        description: Optional[str] = None,
    ):
        dataset = cls()
        dataset.dataset = Dataset.create(
            dataset_name=dataset_name,
            dataset_project=dataset_project,
            dataset_tags=dataset_tags,
            dataset_version=dataset_version,
            output_uri=output_uri,
            description=description,
        )
        return dataset

    def add_files(self, path: Union[str, Path], recursive: bool = True):
        try:
            self.dataset.add_files(
                path, recursive=recursive
            )
        except AttributeError:
            raise AttributeError("Dataset has not been created or initialized.")
