from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi.responses import Response
from pydantic import BaseModel


class IOSchema(BaseModel, ABC):

    media: Optional[List[str]]
    text: Optional[
        Any
    ]  # currently a pydantic bug where dict will always fail to validate

    _response: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def response(self, media_type: Optional[str] = None) -> Response:
        """Return output as response to request

        :return: FastAPI Response to return
        :rtype: Response
        """
        raise NotImplementedError

    class Config:
        underscore_attrs_are_private = True
