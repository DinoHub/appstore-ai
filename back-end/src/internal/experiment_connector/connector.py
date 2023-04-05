"""Provides a base class for all experiment connectors to inherit from.""" ""
from abc import ABC, abstractmethod
from logging import Logger
from typing import Dict, List, Optional

from ...models.model import Artifact


class ExperimentConnector(ABC):
    """Base class for experiment connectors."""

    def __init__(self):
        """Initalize an experiment connector"""
        self.project_name: Optional[str] = None
        self.exp_name: Optional[str] = None
        self.id: Optional[str] = None
        self.output_url: Optional[str] = None
        self.logger: Logger = Logger(__name__)
        self.user: Optional[str] = None

    @property
    @abstractmethod
    def config(self) -> Dict:
        """Returns config associated with experiment

        Raises:
            NotImplementedError: If experiment connector
                does not implement this method.

        Returns:
            Dict: Configuration of experiment
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def tags(self) -> List[str]:
        """Returns tags associated with experiment

        Raises:
            NotImplementedError: If experiment connector
                does not implement this method.

        Returns:
            List: List of tags associated with experiment
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def artifacts(self) -> Dict[str, Artifact]:
        """Returns artifacts associated with experiment

        Raises:
            ValueError: If not currently connected to any experiments
            NotImplementedError: If experiment connector
                does not implement this method.

        Returns:
            Dict[str, Artifact]: Mapping of artifact names to artifacts
        """
        if not self.id:
            raise ValueError("Not currently connected to any experiments")
        raise NotImplementedError

    @property
    @abstractmethod
    def models(self) -> Dict[str, Artifact]:
        """Returns models associated with experiment

        Raises:
            ValueError: If not currently connected to any experiments
            NotImplementedError: If experiment connector
                does not implement this method.

        Returns:
            Dict[str, Artifact]: Mapping of model names to artifacts
        """
        if not self.id:
            raise ValueError("Not currently connected to any experiments")
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def get(cls) -> "ExperimentConnector":
        """Get an existing experiment.

        Raises:
            NotImplementedError: If experiment connector
                does not implement this method.

        Returns:
            ExperimentConnector: Experiment connector
        """
        raise NotImplementedError

    @classmethod
    @abstractmethod
    def clone(
        cls, exp_id: str, clone_name: Optional[str] = None
    ) -> "ExperimentConnector":
        """Clone an existing experiment.

        Args:
            exp_id (str): Id of experiment to clone
            clone_name (Optional[str], optional): Name of cloned experiment. Defaults to None.

        Raises:
            NotImplementedError: If experiment connector
                does not implement this method.

        Returns:
            ExperimentConnector: Cloned experiment connector
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self) -> bool:
        """Delete the experiment.

        Raises:
            NotImplementedError: If experiment connector
                does not implement this method.

        Returns:
            bool: True if experiment was deleted, False otherwise
        """
        raise NotImplementedError

    @abstractmethod
    def close(self):
        """Close the experiment connector.

        Raises:
            NotImplementedError: If experiment connector
                does not implement this method.
        """
        raise NotImplementedError
