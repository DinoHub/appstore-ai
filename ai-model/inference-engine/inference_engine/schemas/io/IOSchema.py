from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from fastapi.responses import Response
from pydantic import BaseModel, validator

from .processors import check_files_exist, check_valid_dict


class IOSchema(BaseModel, ABC):
    """Abstract Class for Input and Output Schemas

    An IOSchema is used to determine how to process
    either the input or output of to the user executor.
    """

    media: Optional[List[str]]
    text: Optional[
        Any
    ]  # currently a pydantic bug where dict will always fail to validate

    _check_file_exists = validator("media", allow_reuse=True, each_item=True)(
        check_files_exist
    )

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
