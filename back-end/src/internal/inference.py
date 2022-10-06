from typing import Dict, List, Optional, Tuple

import httpx
from fastapi import Request, UploadFile


async def stream_response(
    url: str,
    media: Optional[List[UploadFile]] = None,
    text: Optional[str] = None,
):
    if media is not None:
        media.file.seek(0)
    # NOTE: cannot do error handling here due to how fastapi handles exceptions
    # therefore, just have to hope that stream is successful
    files = {"media": [f.file for f in media]} if media is not None else None
    data = {"text": text} if text is not None else None
    async with httpx.AsyncClient(timeout=3600).stream(
        "POST",
        url,
        files=files,
        data=data,
    ) as response:
        response.raise_for_status()
        async for chunk in response.aiter_bytes():
            yield chunk


async def process_inference_data(request: Request) -> Tuple[Dict, Dict]:
    """Take in user data for inference, identify all files and forms,
    putting all file data into a file dict, and ditto for form data into a
    text object

    :param request: _description_
    :type request: Request
    :return: files and text
    :rtype: Tuple[Dict, Dict]
    """
    files = {}
    texts = {}
    form = await request.form()
    async for fieldname, value in form.items():
        if isinstance(value, UploadFile):
            files[fieldname] = value
        else:
            texts[fieldname] = value
    return files, texts
