from typing import Union

from .clearml_dataset import ClearMLDataset

SUPPORTED_CONNECTORS = {"clearml": ClearMLDataset}


class Dataset:
    """Constructor class for different dataset connectors"""

    @staticmethod
    def from_connector(connector_type: str, **kwargs) -> ClearMLDataset:
        """Create a new dataset

        Args:
            connector_type (str): Type of connector to use
            **kwargs: Keyword arguments to pass to connector

        Returns:
            DatasetConnector: Created dataset
        """
        if connector_type not in SUPPORTED_CONNECTORS:
            raise KeyError(
                f"""Dataset connector unsupported.
                Supported connectors: {SUPPORTED_CONNECTORS.keys()}"""
            )
        return SUPPORTED_CONNECTORS[connector_type](**kwargs)
