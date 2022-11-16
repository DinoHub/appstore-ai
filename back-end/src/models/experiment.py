from typing import Union
from enum import Enum

from pydantic import BaseModel


class Connector(str, Enum):
    DEFAULT = ""
    CLEARML = "clearml"
    
class LinkedExperiment(BaseModel):
    connector : Connector 
    experiment_id : str

class ClonePackageModel(BaseModel):
    id: str
    clone_name: Union[str, None] = None
