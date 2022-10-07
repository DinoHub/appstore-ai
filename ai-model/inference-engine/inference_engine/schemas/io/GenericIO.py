import base64
from collections import defaultdict

import filetype
from fastapi.responses import JSONResponse

from .IOSchema import IOSchema


class GenericIO(IOSchema):
    """Generic input schema that accepts both files and json data.
    Can also be used in cases where nothing is provided to a model.

    :param media: List of local file paths to media files
    :type media: List[str]
    :param text: JSON object containing form data
    :type text: Dict[str, Any]
    """

    def response(self) -> JSONResponse:
        """Generic response. Since this could be both text or media,
        our response will be a json response, with any media encoded
        as a base64 string.

        :return: JSONResponse
        :rtype: Response
        """
        response = {}
        if self.media:
            # Encode any media using Base64
            response["media"] = defaultdict(list)
            response["media_types"] = {}
            for field, file_paths in self.media.items():
                for file_path in file_paths:
                    if field not in response["media_types"]:
                        response["media_types"][field] = filetype.guess_mime(
                            file_path
                        )
                    # assume media is list of filenames
                    with open(file_path, "rb") as f:
                        response["media"][field].append(
                            base64.b64encode(f.read()).decode("ascii")
                        )
        if self.text:
            response.update(self.text)
        return JSONResponse(response)
