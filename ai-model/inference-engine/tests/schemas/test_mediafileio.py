import base64
import json
from pathlib import Path
from typing import Any

import pytest
from inference_engine.schemas.io import MediaFileIO


def test_process_uris():
    files = [
        str(
            Path(__file__)
            .parent.parent.joinpath("data", f"image{i}.jpg")
            .absolute()
        )
        for i in (1, 2)
    ]
    schema = MediaFileIO(media=files)
    for file, expected in zip(schema.media, files):
        assert file == expected


def test_response_multi():
    paths = [
        str(
            Path(__file__)
            .parent.parent.joinpath("data", f"image{i}.jpg")
            .absolute()
        )
        for i in range(1, 3)
    ]
    print(paths)
    schema = MediaFileIO(media=paths)
    response = schema.response()
    assert response.media_type == "application/json"
    response_json = json.loads(response.body)
    assert "media" in response_json
    for file in response_json["media"]:
        # Check that it is decodable
        base64.b64decode(file, validate=True)


def test_response_single():
    path = str(
        Path(__file__).parent.parent.joinpath("data", "image1.jpg").absolute()
    )
    schema = MediaFileIO(media=[path])
    response = schema.response()
    assert response.media_type == "image/jpeg"


@pytest.mark.parametrize("input", ["this is a string", 1, True])
@pytest.mark.xfail(reason="Incorrect type")
def test_type_checking(input: Any):
    schema = MediaFileIO(media=input)


@pytest.mark.xfail(reason="Missing input")
def test_missing_media():
    MediaFileIO(media=None)
