from typing import BinaryIO, Dict, List, Optional, Tuple

import httpx
from fastapi import Request, UploadFile
from starlette.datastructures import UploadFile as UploadFileType


async def stream_response(
    url: str,
    media: Optional[List[Tuple[str, Tuple[str, BinaryIO, str]]]] = None,
    text: Optional[Dict[str, str]] = None,
):
    # NOTE: cannot do error handling here due to how fastapi handles exceptions
    # therefore, just have to hope that stream is successful
    async with httpx.AsyncClient(timeout=3600).stream(
        "POST",
        url,
        files=media,
        data=text,
    ) as response:
        response.raise_for_status()
        async for chunk in response.aiter_bytes():
            yield chunk


async def process_inference_data(
    request: Request,
) -> Tuple[List[Tuple[str, Tuple[str, BinaryIO, str]]], Dict]:
    """Process multipart/form data so that files and form data are
    ready to be sent to the Inference Engine.

    :param request: Incoming HTTP request
    :type request: Request
    :return: A list of files and a file data dict to be passed to the Inference Engine
    :rtype: Tuple[List, Dict]
    """
    # NOTE: This is needed as just trying to pass the request body
    # to the IE request call does not work
    files = []
    texts = {}
    form = await request.form()
    for fieldname, value in form.items():
        if isinstance(value, UploadFileType):
            # need to use Starlette UploadFile as it will not be
            # recognized otherwise
            files.append(
                (fieldname, (value.filename, value.file, value.content_type))
            )
        else:
            texts[fieldname] = value
    return files, texts
