import base64
from typing import List, Optional, Union

from fastapi.responses import FileResponse, JSONResponse

from .IOSchema import IOSchema


class MediaFileIO(IOSchema):
    """Input schema when input or output is media files.

    Representation of the media files is a list of strings,
    where each string is the local file path to the media file.

    :param media: List of local file paths to media files
    :type media: List[str]
    """

    media: List[str]

    def response(
        self, media_type: Optional[str] = None
    ) -> Union[FileResponse, JSONResponse]:
        """If multiple media files, will encode in b64, else stream bytes back
        :return: FileResponse
        :rtype: Response

        TODO: Consider other methods (e.g. zip, streaming response)
        """
        if len(self.media) > 1:
            response = {"media": []}
            for file_path in self.media:
                # assume media is list of filenames
                with open(file_path, "rb") as f:
                    response["media"].append(
                        base64.b64encode(f.read()).decode("ascii")
                    )
            response["media_type"] = media_type
            return JSONResponse(response)
        else:
            return FileResponse(self.media[0], media_type=media_type)
