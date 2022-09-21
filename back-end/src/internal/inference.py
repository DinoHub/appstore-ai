import httpx
from fastapi import UploadFile


async def stream_response(media: UploadFile, outputs: str, url: str):
    media.file.seek(0)
    # NOTE: cannot do error handling here due to how fastapi handles exceptions
    # therefore, just have to hope that stream is successful
    async with httpx.AsyncClient().stream(
        "POST",
        url,
        files={"inputs": media.file},
        data={"outputs": outputs},
    ) as response:
        global content_type  # mutate content type globally
        response.raise_for_status()
        content_type = response.headers["Content-Type"]
        async for chunk in response.aiter_bytes():
            yield chunk
