from typing import List, Optional

from fastapi.responses import FileResponse
from pydantic import validator

from .IOSchema import IOSchema
from .processors import check_single_file


class SingleMediaFileIO(IOSchema):
    """Input schema when input or output is just a single media file.
    Representation of the media file is a list containing a single
    string, which is the local file path to the media file.

    :param media: List with single string path to media file
    :type media: List[str]
    """

    media: List[str]

    _check_single_file = validator("media", allow_reuse=True)(
        check_single_file
    )

    def response(self, media_type: Optional[str] = None) -> FileResponse:
        """Stream back media file.
        This and MultipleMediaFileIO are separate as
        there is no way to send back multiple media files
        without either compressing them or encoding
        them in Base64.

        :return: FileResponse
        :rtype: Response
        """

        return FileResponse(self.media[0], media_type=media_type)
