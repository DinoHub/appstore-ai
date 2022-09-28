from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from fastapi.responses import Response
from pydantic import BaseModel


class IOSchema(ABC, BaseModel):

    media = Optional[List[str]]
    text = Optional[Dict]

    @abstractmethod
    def response(self) -> Response:
        """Return output as response to request

        :return: FastAPI Response to return
        :rtype: Response
        """
        raise NotImplementedError
