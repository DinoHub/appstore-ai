from typing import Any

from fastapi.responses import JSONResponse

from .IOSchema import IOSchema


class JSONIO(IOSchema):
    """JSON IO for generic text inputs and outputs.
    Converts any text to a JSON Dictionary

    :param text: JSON object containing form data
    :type text: Dict[str, Any]
    """

    text: Any  # Dict[str, Any]

    def response(self, **kwargs) -> JSONResponse:
        """Send back JSON response.

        :return: JSONResponse
        :rtype: Response
        """
        response = self.text
        return JSONResponse(response)
