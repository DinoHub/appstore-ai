from datetime import datetime
from typing import Dict, List, Optional, Union
from enum import Enum

from pydantic import BaseModel

class Connector(str, Enum):
    DEFAULT = ""
    CLEARML = "clearml"

class LinkedDataset(BaseModel):
    connector : Connector
    dataset_id : str
class DatasetModel(BaseModel):
    id: str
    name: Optional[str]
    created: Optional[datetime]
    tags: Optional[List[str]]
    project: Optional[str]
    files: Optional[Dict]
    default_remote: Optional[str]


class FindDatasetModel(BaseModel):
    id: Optional[Union[str, List[str]]]
    name: Optional[str]
    tags: Optional[List[str]]
    project: Optional[str]
