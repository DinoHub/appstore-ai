from typing import Union

from pydantic import BaseModel


class ClonePackageModel(BaseModel):
    id: str
    clone_name: Union[str, None] = None
