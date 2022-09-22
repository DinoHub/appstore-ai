from .clearml_dataset import ClearMLDataset

SUPPORTED_CONNECTORS = {"clearml": ClearMLDataset}


class Dataset:
    """Constructor class for different dataset connectors"""

    def __new__(cls, connector_type: str):
        if connector_type not in SUPPORTED_CONNECTORS:
            raise KeyError(
                f"""Dataset connector unsupported.
                Supported connectors: {SUPPORTED_CONNECTORS.keys()}"""
            )
        return super().__new__(SUPPORTED_CONNECTORS[connector_type])
