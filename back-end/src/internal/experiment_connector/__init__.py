from .clearml_exp import ClearMLExperiment

SUPPORTED_CONNECTORS = {"clearml": ClearMLExperiment}


class Experiment:
    """Constructor class for different experiment connectors"""

    @staticmethod
    def from_connector(connector_type: str, **kwargs) -> ClearMLExperiment:
        """Create a new experiment

        Args:
            connector_type (str): Type of connector to use
            **kwargs: Keyword arguments to pass to connector

        Returns:
            ExperimentConnector: Created experiment
        """
        if connector_type not in SUPPORTED_CONNECTORS:
            raise KeyError(
                f"""Experiment connector unsupported.
                Supported connectors: {SUPPORTED_CONNECTORS.keys()}"""
            )
        return SUPPORTED_CONNECTORS[connector_type](**kwargs)
