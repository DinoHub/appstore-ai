from typing import Any, Optional

from fastapi.responses import JSONResponse
from pydantic import validator

from .IOSchema import IOSchema
from .processors import check_valid_dict


class JSONIO(IOSchema):
    """JSON IO for generic text inputs and outputs.
    Converts any text to a JSON Dictionary
    :param IOSchema: _description_
    :type IOSchema: _type_
    :return: _description_
    :rtype: _type_
    """

    # media: Optional[List[str]]
    text: Any

    _check_valid_dict = validator("text", allow_reuse=True)(check_valid_dict)

    def response(self) -> JSONResponse:
        """Send back JSON response.

        :return: JSONResponse
        :rtype: Response
        """
        response = self.text
        return JSONResponse(response)
