import base64
from typing import List, Optional

from fastapi.responses import FileResponse
from pydantic import validator

from .IOSchema import IOSchema
from .validators import check_files_exist, check_single_file


class SingleMediaFileIO(IOSchema):
    media = List[str]

    _check_file_exists = validator("media", allow_reuse=True, each_item=True)(
        check_files_exist
    )

    _check_single_file = validator("media", allow_reuse=True)(
        check_single_file
    )

    def response(self) -> FileResponse:
        """Stream back media file.
        This and MultipleMediaFileIO are separate as
        there is no way to send back multiple media files
        without either compressing them or encoding
        them in Base64.

        :return: FileResponse
        :rtype: Response
        """

        return FileResponse(self.media[0])
