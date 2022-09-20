from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union


class DatasetConnector(ABC):
    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def file_entries_dict(self):
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def from_scratch(cls):
        raise NotImplementedError

    @abstractmethod
    def add_files(self, path: Union[str, Path], recursive: bool = True):
        raise NotImplementedError

    @abstractmethod
    def remove_files(self):
        raise NotImplementedError

    @abstractmethod
    def upload(self):
        raise NotImplementedError

    @abstractmethod
    def download(self):
        raise NotImplementedError

    @abstractmethod
    def delete(self):
        raise NotImplementedError
