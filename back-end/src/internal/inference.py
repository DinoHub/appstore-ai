import httpx
from fastapi import UploadFile
from typing import Optional


async def stream_response(
    outputs: str,
    url: str,
    media: Optional[UploadFile] = None,
    text: Optional[str] = None,
):
    media.file.seek(0)
    # NOTE: cannot do error handling here due to how fastapi handles exceptions
    # therefore, just have to hope that stream is successful
    files = {"inputs": media.file} if media is not None else None
    data = {"outputs": outputs}
    if text is not None:
        data["inputs"] = text
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
