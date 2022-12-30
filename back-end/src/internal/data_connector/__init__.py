"""This module contains the Dataset Connector classes,
which provides a common interface to allow the app
to interact with different providers (e.g ClearML datasets,
Weights and Biases artifacts, DVC, etc.).
"""
from ...models.dataset import Connector
from .clearml_dataset import ClearMLDataset

# NOTE: Update type hinting when more connectors are added
SUPPORTED_CONNECTORS = {"clearml": ClearMLDataset}


class Dataset:
    """Constructor class for different dataset connectors"""

    @staticmethod
    def from_connector(connector_type: Connector, **kwargs) -> ClearMLDataset:
        """Create a new dataset

        Args:
            connector_type (Connector): Type of connector to use
            **kwargs: Keyword arguments to pass to connector

        Raises:
            KeyError: If connector type is not supported

        Returns:
            DatasetConnector: Created dataset
        """
        if connector_type not in SUPPORTED_CONNECTORS:
            raise KeyError(
                f"""Dataset connector unsupported.
                Supported connectors: {SUPPORTED_CONNECTORS.keys()}"""
            )
        return SUPPORTED_CONNECTORS[connector_type](**kwargs)
