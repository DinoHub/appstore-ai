from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict, List, Optional


class ExperimentConnector(ABC):
    def __init__(self):
        """Initalize an experiment connector"""
        self.project_name: Optional[str] = None
        self.exp_name: Optional[str] = None
        self.id: Optional[str] = None
        self.logger: Logger = Logger(__name__)
        self.user: Optional[str] = None

    @property
    @abstractmethod
    def config(self) -> Dict:
        """Return config object associated with experiment
        :return: _description_
        :rtype: Dict
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def tags(self) -> List:
        """Return tags associated with experiment
        :return: _description_
        :rtype: Dict
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def artifacts(self) -> Dict:
        """Returns artifact metadata

        :raises ValueError: _description_
        :return: _description_
        :rtype: Dict
        """
        if not self.id:
            raise ValueError("Not currently connected to any experiments")
        raise NotImplementedError

    @property
    @abstractmethod
    def models(self) -> Dict:
        """Returns model metadata

        :raises ValueError: _description_
        :return: _description_
        :rtype: Dict
        """
        if not self.id:
            raise ValueError("Not currently connected to any experiments")
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get(cls) -> "ExperimentConnector":
        """Get an existing experiment.

        :return: _description_
        :rtype: ExperimentConnector
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def clone(
        cls, exp_id: str, clone_name: Optional[str] = None
    ) -> "ExperimentConnector":
        """Clone an existing experiment.

        :param exp_id: _description_
        :type exp_id: str
        :param clone_name: _description_, defaults to None
        :type clone_name: Optional[str], optional
        :return: _description_
        :rtype: ExperimentConnector
        """
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Close the experiment"""
        raise NotImplementedError