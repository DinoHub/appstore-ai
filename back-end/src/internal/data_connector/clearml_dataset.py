"""ClearML Dataset Connector
A interface to interact with ClearML datasets.
"""
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Union

from clearml import Dataset, Task

from ...models.common import Artifact
from .connector import DatasetConnector


class ClearMLDataset(DatasetConnector):
    """ClearML Dataset Connector."""

    def __init__(self):
        """Initialize a ClearML dataset connector.
        Note: Do not directly instantiate,
        instead, you should use the `create`
        or `get` class method to create the
        connector.
        """
        super().__init__()
        self.dataset: Optional[Dataset] = None
        self.output_path: Optional[Union[Path, str]] = None
        self._task: Optional[Task] = None

    @property
    def file_entries(self) -> Dict:
        if self.dataset is None:
            raise AttributeError("Dataset has not been initialized")
        return self.dataset.file_entries_dict  # type: ignore

    @property
    def artifacts(self) -> List[Artifact]:
        """Get a list of artifacts in the dataset.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.

        Returns:
            List[Artifact]: List of artifacts in the dataset
        """
        if self.dataset is None:
            raise AttributeError("Dataset has not been initialized")
        data = []
        if not self._task:
            self._task = Task.get_task(task_id=self.dataset.id)
        for name, entry in self._task.artifacts.items():
            data.append(
                Artifact(artifactType="dataset", name=name, url=entry.url)
            )
        return data

    @property
    def name(self) -> str:
        if self.dataset is None:
            raise AttributeError("Dataset has not been initialized")
        return self.dataset.name

    @property
    def project(self) -> str:
        if self.dataset is None:
            raise AttributeError("Dataset has not been initialized")
        return self.dataset.project

    @property
    def tags(self) -> List[str]:
        """Get the tags associated with the dataset.

        Raises:
            AttributeError: If dataset has not been initialized.

        Returns:
            List[str]: List of tags associated with the dataset.
        """
        if self.dataset is None:
            raise AttributeError("Dataset has not been initialized")
        return self.dataset.tags

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
        try:
            dataset._task = Task.get_task(task_id=dataset.id)
        except Exception:
            pass
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
            partial_name=partial_name,
            dataset_project=project,
            ids=ids,
            tags=tags,
        )

    def add_files(
        self, path: Union[str, Path], recursive: bool = True
    ) -> None:
        if self.dataset is None:
            raise AttributeError("Dataset has not been created.")
        self.dataset.add_files(path=path, recursive=recursive)

    def remove_files(
        self, path: Union[str, Path], recursive: bool = True
    ) -> None:
        if self.dataset is None:
            raise AttributeError("Dataset has not been created.")
        self.dataset.remove_files(dataset_path=str(path), recursive=recursive)

    def upload(self, remote: Optional[str] = None) -> None:
        if self.dataset is None:
            raise AttributeError("Dataset has not been created.")
        if remote is None:
            if self.default_remote is None:
                warning_msg = "No remote url specified, using default file server specified in clearml_conf"
            else:
                warning_msg = f"No remote url specified, using default remote of {self.default_remote}"
            self.logger.warning(warning_msg)
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
        if self.output_path is None:
            raise RuntimeError("Failed to download dataset")
        return self.output_path

    def delete(self) -> None:
        # If dataset does not exist, then
        # no need to do anything
        if self.dataset is not None:
            self.dataset.delete(dataset_id=self.id)
