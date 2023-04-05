"""Data models for experiment related endpoints.""" ""
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from ..models.common import Artifact


class Connector(str, Enum):
    """Allowed connectors for experiments."""

    DEFAULT = ""
    CLEARML = "clearml"


class LinkedExperiment(BaseModel):
    """Linked experiment model from model creation/update process."""

    connector: Connector
    experiment_id: str = Field(..., alias="experimentId")
    output_url: Optional[str] = Field(default="", alias="outputUrl")

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys."""

        allow_population_by_field_name = True


class ExperimentResponse(BaseModel):
    """Response model for getting an experiment."""

    id: str
    owner: str
    name: str
    project_name: str
    output_url: Optional[str]
    tags: List[str]
    frameworks: List[str]
    config: dict
    scalars: Optional[List[dict]] = None
    plots: Optional[List[dict]] = None
    artifacts: Optional[Dict[str, Artifact]] = None


class ClonePackageModel(BaseModel):
    """Model for cloning a experiment. Currently unused."""

    id: str
    clone_name: Union[str, None] = None
