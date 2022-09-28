from typing import Dict, List, Optional

from fastapi.responses import JSONResponse

from .IOSchema import IOSchema


class TextIO(IOSchema):
    """Text IO for generic text inputs and outputs.
    To store more complex data, consider
    stringifying the JSON file

    :param IOSchema: _description_
    :type IOSchema: _type_
    :return: _description_
    :rtype: _type_
    """

    media = Optional[List[str]]
    text = Optional[Dict]

    def response(self) -> JSONResponse:
        """Send back JSON response.

        :return: JSONResponse
        :rtype: Response
        """
        response = self.text
        return JSONResponse(response)
