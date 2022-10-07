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

    # currently a pydantic bug where dict will always fail to validate
    media: Optional[Any]  # Optional[Dict[str, List[str]]]
    text: Optional[Any]  # Optional[Dict[str, Any]]

    _check_valid_dict = validator("text", "media", allow_reuse=True)(
        check_valid_dict
    )
    _check_file_exists = validator("media", allow_reuse=True, each_item=True)(
        check_files_exist
    )

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @abstractmethod
    def response(self) -> Response:
        """Return output as response to request

        :return: FastAPI Response to return
        :rtype: Response
        """
        raise NotImplementedError

    class Config:
        underscore_attrs_are_private = True  # hide validators from schema
