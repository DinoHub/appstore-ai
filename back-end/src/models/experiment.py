from typing import Union
from enum import Enum

from pydantic import BaseModel
from ..internal.utils import to_camel_case


class Connector(str, Enum):
    DEFAULT = ""
    CLEARML = "clearml"
    
class LinkedExperiment(BaseModel):
    connector : Connector 
    experiment_id : str
    class Config:
        alias_generator = to_camel_case
class ClonePackageModel(BaseModel):
    id: str
    clone_name: Union[str, None] = None
