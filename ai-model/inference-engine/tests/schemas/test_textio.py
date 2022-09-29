import json
from typing import Any, Dict, Union

import pytest
from inference_engine.schemas.io import TextIO


def test_create_io():
    TextIO(text="Hello World")


@pytest.mark.parametrize(
    "input,expected", [("Hello World", "Hello World"), ({"text": "Hi"}, "Hi")]
)
def test_process_text(input: Union[str, Dict[str, str]], expected: str):
    schema = TextIO(text=input)
    assert schema.text == expected


def test_response():
    schema = TextIO(text="Hello world")
    response = schema.response()
    response_json = json.loads(response.body)
    assert response.media_type == "application/json"
    assert response_json["text"] == "Hello world"


@pytest.mark.parametrize("input", [513, {"hello there": "tea"}])
@pytest.mark.xfail(reason="Incorrect type")
def test_type_checking(input: Any):
    schema = TextIO(text=input)


@pytest.mark.xfail(reason="Missing text")
def test_missing_text():
    TextIO(text=None)
