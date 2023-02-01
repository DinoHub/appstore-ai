"""Provides a base class for all dataset connectors to inherit from."""
from abc import ABC, abstractmethod
from logging import Logger
from pathlib import Path
from typing import Dict, List, Optional, Union

from ...models.common import Artifact


class DatasetConnector(ABC):
    """Base class for dataset connectors."""

    def __init__(self):
        """Initialize a dataset connector.

        WARNING: Do not directly instantiate,
        instead, you should use the `create`
        or `get` class method to create the
        connector.
        """
        self.dataset = None
        self.default_remote: Optional[str] = None
        self.id: Optional[str] = None
        self.logger: Logger = Logger(__name__)

    @property
    @abstractmethod
    def file_entries(self) -> Dict:
        """Get a dictionary of files in the dataset.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.

        Returns:
            Dict: Dictionary of files in the dataset
        """
        raise NotImplementedError(
            "Connector does not have file entries attribute defined."
        )

    @property
    @abstractmethod
    def artifacts(self) -> List[Artifact]:
        """Get a list of artifacts in the dataset.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.

        Returns:
            List[Artifact]: List of artifacts in the dataset
        """
        raise NotImplementedError(
            "Connector does not have file entries attribute defined."
        )

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name of the dataset.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.

        Returns:
            str: Name of the dataset
        """
        raise NotImplementedError(
            "Connector does not have file entries attribute defined."
        )

    @property
    @abstractmethod
    def project(self) -> str:
        """Get the project associated with the dataset.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.

        Returns:
            str: Project associated with the dataset
        """
        raise NotImplementedError(
            "Connector does not have file entries attribute defined."
        )

    @classmethod
    @abstractmethod
    def get(cls) -> "DatasetConnector":
        """Get an existing dataset, but
        do not download contents of dataset.

        This method should return a properly
        initialized DatasetConnector with the
        .dataset attribute set.

        Returns:
            DatasetConnector: Created dataset
        """
        ds = cls()
        ds.dataset = None
        return ds

    @classmethod
    @abstractmethod
    def create(cls, name: str, version: str = "latest") -> "DatasetConnector":
        """Create a dataset from scratch.
        Note that user will have to add files
        after the dataset has been created.

        Args:
            name (str): Name of the dataset
            version (str, optional): Version to give dataset. Defaults to "latest".

        Returns:
            DatasetConnector: Created dataset
        """
        ds = cls()
        ds.dataset = None
        return ds

    @abstractmethod
    def add_files(
        self, path: Union[str, Path], recursive: bool = True
    ) -> None:
        """Add files to a dataset.

        Args:
            path (Union[str, Path]): Local/remote path to data you want to add
            recursive (bool, optional): Recursively add sub-files/folders?.
                Defaults to True.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def remove_files(
        self, path: Union[str, Path], recursive: bool = True
    ) -> None:
        """Remove files from a dataset.

        Args:
            path (Union[str, Path]): Local/remote path to data you want to remove
            recursive (bool, optional): Recursively add sub-files/folders?. Defaults to True.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.
        """
        raise NotImplementedError

    @abstractmethod
    def upload(self, remote: Optional[str] = None) -> None:
        """Push changes to remote.

        Args:
            remote (Optional[str]): URL to push files to.
                If None, will use any pre-defined URL in the dataset.
                Defaults to None.

        Raises:
            ValueError: If remote is not defined in arguments
                and dataset has no default remote, a ValueError
                should be raised

            NotImplementedError: If dataset connector
                does not implement this method.
        """
        if remote is None and self.default_remote is None:
            raise ValueError
        raise NotImplementedError

    @abstractmethod
    def download(self, path: Union[str, Path], overwrite: bool = True) -> str:
        """Downloads mutable copy of entire dataset.

        Args:
            path (Union[str, Path]): Target folder to download dataset to
            overwrite (bool, optional): If existing files in target folder should be removed.
                Defaults to True.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.

        Returns:
            str: File path to downloaded dataset
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self) -> None:
        """Delete dataset.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.
        """
        raise NotImplementedError

    @staticmethod
    @abstractmethod
    def list_datasets() -> List[Dict]:
        """Obtain a list of all datasets, based on
            what is available to the dataset connector.

        Raises:
            NotImplementedError: If dataset connector
                does not implement this method.

        Returns:
            List[Dict]: List of dictionaries containing dataset metadata
        """
        raise NotImplementedError
