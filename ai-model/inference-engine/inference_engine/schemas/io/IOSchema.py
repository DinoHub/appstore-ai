from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi.responses import Response
from pydantic import BaseModel


class IOSchema(BaseModel, ABC):

    media: Optional[List[str]]
    text: Optional[
        Any
    ]  # currently a pydantic bug where dict will always fail to validate

    @abstractmethod
    def response(self) -> Response:
        """Return output as response to request

        :return: FastAPI Response to return
        :rtype: Response
        """
        raise NotImplementedError

    class Config:
        arbitrary_types_allowed = True
