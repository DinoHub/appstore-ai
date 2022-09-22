from .clearml_dataset import ClearMLDataset


class Dataset:
    def __new__(cls, connector_type: str):
        SUPPORTED_CONNECTORS = {
            "clearml" : ClearMLDataset
        }
        if connector_type not in SUPPORTED_CONNECTORS:
            raise KeyError(
                f"""Dataset connector unsupported.
                Supported connectors: {SUPPORTED_CONNECTORS.keys()}"""
            )
        return super().__new__(
            SUPPORTED_CONNECTORS[connector_type]
        )