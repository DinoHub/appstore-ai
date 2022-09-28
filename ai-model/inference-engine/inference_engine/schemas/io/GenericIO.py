import base64
from typing import Dict, List, Optional

from fastapi.responses import JSONResponse
from pydantic import validator
from starlette.background import BackgroundTask

from ...utils.io import remove_unused_files
from .IOSchema import IOSchema
from .validators import check_files_exist


class GenericIO(IOSchema):
    """Generic input schema that accepts both files and json data.
    :param IOSchema: _description_
    :type IOSchema: _type_
    :return: _description_
    :rtype: _type_
    """

    media = Optional[List[str]]
    text = Optional[Dict]

    _check_file_exists = validator("media", allow_reuse=True, each_item=True)(
        check_files_exist
    )

    def response(self) -> JSONResponse:
        """Generic response. Since this could be both text or media,
        our response will be a json response, with any media encoded
        as a base64 string.

        :return: JSONResponse
        :rtype: Response

        TODO: Consider putting json in header, and media in response
        (potential flaws: unable to send multiple media files without zipping,
        makes back-end processing code more complex)
        """
        response = {}
        if self.media:
            # Encode any media using Base64
            response["media"] = []
            for file_path in self.media:
                # assume media is list of filenames
                with open(file_path, "rb") as f:
                    response["media"].append(base64.b64encode(f.read()))
        if self.text:
            response.update(self.text)

        return JSONResponse(response)
