from typing import Union
from enum import Enum

from pydantic import BaseModel


class Connector(str, Enum):
    CLEARML = "clearml"


class ClonePackageModel(BaseModel):
    id: str
    clone_name: Union[str, None] = None
