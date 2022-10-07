import json
from collections import defaultdict
from io import BytesIO
from typing import List

import aiohttp
import httpx
import requests
import uvicorn
from fastapi import FastAPI, File, Form, Request, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from starlette.datastructures import UploadFile as StarletteUploadFile

app = FastAPI()


@app.get("/")
def hello_world():
    return {"message": "hello world"}


async def stream_generator(response: httpx.Response):
    async for chunk in response.aiter_bytes():
        yield chunk


@app.post("/")
async def multiple_fields(
    req: Request,
    image_1: List[UploadFile],
    image_2: List[UploadFile],
    text: str = Form(...),
):
    files = []
    forms = {}
    file_fields = set()
    text_fields = set()
    form = await req.form()
    for fieldname, value in form.items():
        if isinstance(value, StarletteUploadFile):
            print("Add")
            file_fields.add(fieldname)
            files.append(
                (fieldname, (value.filename, value.file, value.content_type))
            )
        else:
            text_fields.add(fieldname)
            forms[fieldname] = value
    # with requests.post(
    #     "http://localhost:4090/fake_ie",
    #     files=files,
    #     data=forms,
    #     stream=True
    # ) as r:
    #     return StreamingResponse(
    #         content=r.iter_content(),
    #         # media_type=r.headers["Content-Type"]
    #         media_type="image/jpeg"
    #     )
    # async with aiohttp.ClientSession() as session:
    #     form = aiohttp.FormData()
    #     form.add_field(
    #         "image_1", files[0][1][1].read(), content_type=files[0][1][2], filename=files[0][1][0]
    #     )
    #     async with session.post("http://localhost:4090/fake_ie", data=form) as r:
    #         return StreamingResponse(
    #             r.content.__aiter__(),
    #             # media_type=r.headers["Content-Type"]
    #         )
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:4090/fake_ie",
            files=files,
            data=forms,
            timeout=60,
        )
        return StreamingResponse(
            BytesIO(response.content),
            media_type=response.headers.get("Content-Type"),
        )
    # return response.json()
    # async with httpx.AsyncClient().stream("POST","http://localhost:4090/fake_ie", files=files,data=forms) as stream:
    #     return StreamingResponse(
    #         stream.aiter_raw(),
    #         media_type=stream.headers["Content-Type"]
    #     )


from tempfile import NamedTemporaryFile

CHUNK_SIZE = 1024


def download_file(file: UploadFile = File()) -> str:
    """Download file that has been sent by the request.

    We generate a unique filename for each file, that still contains
    the original filename. This is useful in cases where,
    the filename contains information (e.g a category, formfield).

    :param file: File to be written locally, defaults to File()
    :type file: UploadFile, optional
    :return: File path to the downloaded file
    :rtype: str
    """
    # Generate a filename
    ext = file.filename.split(".")[-1]
    with NamedTemporaryFile(delete=False, suffix=f".{ext}") as f:
        while content := file.file.read(CHUNK_SIZE):
            f.write(content)
        filename = f.name
    return filename


@app.post("/fake_ie")
async def fake_ie(req: Request):
    print("Recievied request")
    req_data = await req.form()
    text = defaultdict(list)
    media = defaultdict(list)

    for fieldname, value in req_data.items():
        print("here")
        if isinstance(value, StarletteUploadFile):
            media[fieldname].append(value)
        else:
            text[fieldname].append(value)

    for k, v in media.items():
        print("here2")
        media[k] = [download_file(file) for file in v]
    # try:

    # for k, v in text.items():
    #     try:
    #         text[k] = json.loads(v)
    #     except json.JSONDecodeError:
    #         text[k] = v
    return FileResponse(media["image_1"][0])
    # import base64

    # return {
    #     "media" : base64.b64encode(open(media["image_1"][0], "rb").read()).decode("ascii")
    # }


if __name__ == "__main__":
    uvicorn.run("prototype:app", port=4090, workers=2)
