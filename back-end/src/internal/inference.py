from typing import List, Optional

import httpx
from fastapi import UploadFile


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
