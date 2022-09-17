from abc import ABC, abstractmethod


class DatasetConnector(ABC):

    @property
    @abstractmethod
    def id(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def file_entries_dict(self):
        raise NotImplementedError

    @abstractmethod
    def create(self):
        raise NotImplementedError

    @abstractmethod
    def add_files(self):
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