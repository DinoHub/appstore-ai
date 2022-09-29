import json
from typing import Any, Dict

import pytest
from inference_engine.schemas.io import JSONIO


def test_create_io():
    JSONIO(text={"message": "hello world"})


@pytest.mark.parametrize("input,expected", [({"message": "Hi"}, "Hi")])
def test_process_text(input: Dict[str, str], expected: str):
    schema = JSONIO(text=input)
    assert schema.text["message"] == expected


def test_response():
    schema = JSONIO(text={"message": "hello world"})
    response = schema.response()
    response_json = json.loads(response.body)
    assert response.media_type == "application/json"
    assert response_json["message"] == "hello world"


@pytest.mark.parametrize("input", ["this is a string", 1, True])
@pytest.mark.xfail(reason="Incorrect type")
def test_type_checking(input: Any):
    schema = JSONIO(text=input)


@pytest.mark.xfail(reason="Missing input")
def test_missing_text():
    JSONIO(text=None)
