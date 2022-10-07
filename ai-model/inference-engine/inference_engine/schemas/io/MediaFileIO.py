import base64
from collections import defaultdict
from typing import Any, Union

import filetype
from fastapi.responses import FileResponse, JSONResponse

from .IOSchema import IOSchema


class MediaFileIO(IOSchema):
    """Input schema when input or output is media files.

    :param media: Dict where keys are field names, and values are list of file paths for those fields
    :type media: Dict[str, List[str]]
    """

    media: Any  # Dict[str, List[str]]

    def response(self) -> Union[FileResponse, JSONResponse]:
        """If multiple media files, will encode in b64, else stream bytes back
        :return: Union[FileResponse, JSONResponse]
        :rtype: Response
        """
        if len(self.media) == 1 and len(list(self.media.values())[0]) == 1:
            file = list(self.media.values())[0]
            mime_type = filetype.guess_mime(file)
            return FileResponse(file, media_type=mime_type)
        else:
            response = {"media": defaultdict(list), "media_types": {}}
            for field, file_paths in self.media.items():
                for file_path in file_paths:
                    if field not in response["media_types"]:
                        response["media_types"][field] = filetype.guess_mime(
                            file_path
                        )
                    with open(file_path, "rb") as f:
                        response["media"][field].append(
                            base64.b64encode(f.read()).decode("ascii")
                        )

            return JSONResponse(response)
