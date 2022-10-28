from .clearml_exp import ClearMLExperiment

SUPPORTED_CONNECTORS = {"clearml": ClearMLExperiment}


class Experiment:
    """Constructor class for different experiment connectors"""

    def __new__(cls, connector_type: str):
        if connector_type not in SUPPORTED_CONNECTORS:
            raise KeyError(
                f"""Experiment connector unsupported.
                Supported connectors: {SUPPORTED_CONNECTORS.keys()}"""
            )
        return super().__new__(SUPPORTED_CONNECTORS[connector_type])

