from typing import Union
from enum import Enum

from pydantic import BaseModel, Field
from ..internal.utils import to_camel_case


class Connector(str, Enum):
    DEFAULT = ""
    CLEARML = "clearml"
    
class LinkedExperiment(BaseModel):
    connector : Connector 
    experiment_id : str  = Field(..., alias="experimentId")
    class Config:
        allow_population_by_field_name = True

class ClonePackageModel(BaseModel):
    id: str
    clone_name: Union[str, None] = None
