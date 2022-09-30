import base64
from typing import List, Optional

from fastapi.responses import JSONResponse
from pydantic import validator

from .IOSchema import IOSchema
from .processors import check_files_exist


class MultipleMediaFileIO(IOSchema):
    """Input schema when input or output is multiple media files.

    Representation of the media files is a list of strings,
    where each string is the local file path to the media file.

    :param media: List of local file paths to media files
    :type media: List[str]
    """

    media: List[str]

    _check_file_exists = validator("media", allow_reuse=True, each_item=True)(
        check_files_exist
    )

    def response(self, media_type: Optional[str] = None) -> JSONResponse:
        """Stream back media files.
        :return: FileResponse
        :rtype: Response

        TODO: Consider other methods (e.g. zip, streaming response)
        """
        response = {"media": []}
        for file_path in self.media:
            # assume media is list of filenames
            with open(file_path, "rb") as f:
                response["media"].append(
                    base64.b64encode(f.read()).decode("ascii")
                )
        response["media_type"] = media_type
        return JSONResponse(response)
