from abc import ABC, abstractmethod
from typing import Dict

from fastapi.responses import Response
from pydantic import BaseModel


class IOSchema(ABC, BaseModel):
    @abstractmethod
    def response(self) -> Response:
        """Return output as response to request

        :return: FastAPI Response to return
        :rtype: Response
        """
        raise NotImplementedError
