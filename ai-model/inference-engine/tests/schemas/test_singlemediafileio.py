from pathlib import Path
from typing import Any

import pytest
from inference_engine.schemas.io import SingleMediaFileIO


def test_process_uris():
    path = str(
        Path(__file__).parent.parent.joinpath("data", "image1.jpg").absolute()
    )
    schema = SingleMediaFileIO(media=[path])
    assert schema.media[0] == path


def test_response():
    path = str(
        Path(__file__).parent.parent.joinpath("data", "image1.jpg").absolute()
    )
    schema = SingleMediaFileIO(media=[path])
    response = schema.response()
    assert response.media_type == "image/jpeg"


@pytest.mark.xfail(reason="Multiple inputs provided")
def test_multiple_files():
    files = [
        str(
            Path(__file__)
            .parent.parent.joinpath("data", f"image{i}.jpg")
            .absolute()
        )
        for i in (1, 2)
    ]
    schema = SingleMediaFileIO(media=files)


@pytest.mark.parametrize("input", ["this is a string", 1, True])
@pytest.mark.xfail(reason="Incorrect type")
def test_type_checking(input: Any):
    schema = SingleMediaFileIO(media=input)


@pytest.mark.xfail(reason="Missing input")
def test_missing_media():
    SingleMediaFileIO(media=None)
