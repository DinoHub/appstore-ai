"""Data models for datasets."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field

from .common import Artifact


class Connector(str, Enum):
    """Allowed connectors for datasets."""

    DEFAULT = ""
    CLEARML = "clearml"


class LinkedDataset(BaseModel):
    """Linked dataset model from model creation/update process."""

    connector: Connector
    dataset_id: str = Field(..., alias="datasetId")

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys."""

        allow_population_by_field_name = True


class DatasetModel(BaseModel):
    """Dataset model."""

    id: str
    name: Optional[str] = None
    created: Optional[datetime] = None
    tags: Optional[List[str]] = None
    project: Optional[str] = None
    files: Optional[Dict] = None
    default_remote: Optional[str] = None
    artifacts: Optional[List[Artifact]] = None


class FindDatasetModel(BaseModel):
    """Request model for finding datasets."""

    id: Optional[Union[str, List[str]]] = None
    name: Optional[str] = None
    tags: Optional[List[str]] = None
    project: Optional[str] = None
