from io import BytesIO
from typing import BinaryIO, Dict, List, Optional, Tuple

import httpx
from fastapi import Request, UploadFile
from fastapi.responses import StreamingResponse
from starlette.datastructures import UploadFile as UploadFileType


async def stream_generator(
    inference_url: str, media_data: List, form_data: Dict
):
    async with httpx.AsyncClient() as client:
        async with client.stream(
            "POST",
            f"{inference_url}/predict",
            files=media_data,
            data=form_data,
        ) as resp:
            async for chunk in resp.aiter_bytes():
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
