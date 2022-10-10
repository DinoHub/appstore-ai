import base64
import json
from pathlib import Path
from typing import Any, Dict

import pytest
from inference_engine.schemas.io import GenericIO


@pytest.mark.parametrize("input,expected", [({"message": "Hi"}, "Hi")])
def test_process_text(input: Dict[str, str], expected: str):
    schema = GenericIO(text=input)
    assert schema.text["message"] == expected


def test_process_uris():
    files = [
        str(
            Path(__file__)
            .parent.parent.joinpath("data", f"image{i}.jpg")
            .absolute()
        )
        for i in (1, 2)
    ]
    schema = GenericIO(media={"files": files})
    for file, expected in zip(schema.media["files"], files):
        assert file == expected


def test_response():
    path = str(
        Path(__file__).parent.parent.joinpath("data", "image1.jpg").absolute()
    )
    schema = GenericIO(media={"files": [path]}, text={"text": "hello world"})
    response = schema.response()
    assert response.media_type == "application/json"
    response_json = json.loads(response.body)
    assert response_json["text"] == "hello world"
    assert "media" in response_json
    for file in response_json["media"]["files"]:
        # Check that it is decodable
        base64.b64decode(file, validate=True)


@pytest.mark.parametrize(
    "media_input,text_input",
    [
        ("this is a string", 1),
        (True, "Valid string"),
        (["valid file type"], False),
    ],
)
@pytest.mark.xfail(reason="Incorrect type")
def test_type_checking(media_input: Any, text_input: Any):
    schema = GenericIO(text=text_input, media=media_input)


@pytest.mark.xfail(reason="Missing input")
def test_missing_inputs():
    GenericIO(media=None, text=None)
