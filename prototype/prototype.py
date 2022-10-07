import json
from collections import defaultdict
from typing import List

import httpx
import requests
import uvicorn
from fastapi import FastAPI, File, Form, Request, UploadFile
from starlette.datastructures import UploadFile as StarletteUploadFile

app = FastAPI()


@app.get("/")
def hello_world():
    return {"message": "hello world"}


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
    with httpx.Client() as client:
        response = client.post(
            "http://localhost:4090/fake_ie",
            files=files,
            data=forms,
            timeout=60,
        )
    return response.json()


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
    with NamedTemporaryFile(delete=False) as f:
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
    return {"blob": media, "json": text}


if __name__ == "__main__":
    uvicorn.run("prototype:app", port=4090, workers=2)
