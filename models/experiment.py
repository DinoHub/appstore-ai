from typing import Union

from pydantic import BaseModel


class ClonePackage(BaseModel):
    id: str
    clone_name: Union[str, None] = None