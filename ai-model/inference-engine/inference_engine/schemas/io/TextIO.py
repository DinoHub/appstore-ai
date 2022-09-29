from typing import Any, Optional

from fastapi.responses import JSONResponse
from pydantic import validator

from .IOSchema import IOSchema
from .processors import process_text


class TextIO(IOSchema):
    """Text IO which simplifies the input
    of plain text to just using the `.text`
    method to get the text. For storing more,
    use the JSONIO schema.

    :param IOSchema: _description_
    :type IOSchema: _type_
    :return: _description_
    :rtype: _type_
    """

    # media: Optional[List[str]]
    text: Any

    _process_text = validator("text", allow_reuse=True)(process_text)

    def response(self) -> JSONResponse:
        """Send back JSON response.

        :return: JSONResponse
        :rtype: Response
        """
        response = dict(text=self.text)
        return JSONResponse(response)
