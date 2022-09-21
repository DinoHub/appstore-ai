from typing import Optional

import httpx
from fastapi import UploadFile


async def stream_response(
    url: str,
    outputs: Optional[str] = None,
    media: Optional[UploadFile] = None,
    text: Optional[str] = None,
):
    media.file.seek(0)
    # NOTE: cannot do error handling here due to how fastapi handles exceptions
    # therefore, just have to hope that stream is successful
    files = {"media": media.file} if media is not None else None
    data = {"outputs": outputs, "text" : text }
    async with httpx.AsyncClient().stream(
        "POST",
        url,
        files=files,
        data=data,
    ) as response:
        global content_type  # mutate content type globally
        response.raise_for_status()
        content_type = response.headers["Content-Type"]
        async for chunk in response.aiter_bytes():
            yield chunk
