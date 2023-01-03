"""This module contains the experiment connector classes,
which provides a common interface to allow the app
to interact with different providers (e.g ClearML experiments,
Weights and Biases runs, DVC, etc.)"""

from ...models.experiment import Connector
from .clearml_exp import ClearMLExperiment

SUPPORTED_CONNECTORS = {"clearml": ClearMLExperiment}


class Experiment:
    """Constructor class for different experiment connectors"""

    @staticmethod
    def from_connector(
        connector_type: Connector, **kwargs
    ) -> ClearMLExperiment:
        """Create a new experiment

        Args:
            connector_type (Connector): Type of connector to use
            **kwargs: Keyword arguments to pass to connector

        Raises:
            KeyError: If connector type is not supported

        Returns:
            ExperimentConnector: Created experiment
        """
        if connector_type not in SUPPORTED_CONNECTORS:
            raise KeyError(
                f"""Experiment connector unsupported.
                Supported connectors: {SUPPORTED_CONNECTORS.keys()}"""
            )
        return SUPPORTED_CONNECTORS[connector_type](**kwargs)
