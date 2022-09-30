from typing import Any, Optional

from fastapi.responses import JSONResponse
from pydantic import validator

from .IOSchema import IOSchema
from .processors import check_valid_dict


class JSONIO(IOSchema):
    """JSON IO for generic text inputs and outputs.
    Converts any text to a JSON Dictionary

    :param text: JSON object containing form data
    :type text: Dict[str, Any]
    """

    # media: Optional[List[str]]
    text: Any

    _check_valid_dict = validator("text", allow_reuse=True)(check_valid_dict)

    def response(self, **kwargs) -> JSONResponse:
        """Send back JSON response.

        :return: JSONResponse
        :rtype: Response
        """
        response = self.text
        return JSONResponse(response)
