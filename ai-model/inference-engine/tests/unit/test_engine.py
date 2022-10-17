from pathlib import Path
from typing import Dict

from inference_engine.core.engine import InferenceEngine
from inference_engine.schemas.io import GenericIO, TextIO
from yaml import safe_load


def test_create_engine():
    engine = InferenceEngine()


def test_create_engine_from_dict():
    config = {
        "schema_version": 2,
        "metadata": {
            "name": "Example Engine",
            "version": "v1",
            "description": "Test",
            "author": "Test",
        },
        "endpoints": {
            "predict": {
                "type": "POST",
                "input_schema": "MediaFileIO",
                "output_schema": "MediaFileIO",
            }
        },
    }

    engine = InferenceEngine.from_dict(config)
    for key, value in config["metadata"].items():
        assert getattr(engine, key) == value
    assert config["endpoints"] == engine.endpoint_metas


def test_create_engine_from_yaml():
    path = str(
        Path(__file__).parent.parent.joinpath("data", "meta.yml").absolute()
    )
    engine = InferenceEngine.from_yaml(path)
    config: Dict = safe_load(open(path, "r"))
    for key, value in config["metadata"].items():
        assert getattr(engine, key) == value
    assert config["endpoints"] == engine.endpoint_metas


def test_register_endpoint():
    engine = InferenceEngine()

    def hello_world(data: GenericIO) -> TextIO:
        return TextIO(text="hello world!")

    engine._register(
        "helloworld",
        func=hello_world,
        input_schema=GenericIO,
        output_schema=TextIO,
    )
    assert "helloworld" in engine.endpoint_metas
    assert engine.endpoint_metas["helloworld"]["type"] == "POST"
    assert engine.endpoint_metas["helloworld"]["input_schema"] == "GenericIO"
    assert engine.endpoint_metas["helloworld"]["output_schema"] == "TextIO"


def test_override_endpoint_metadata():
    engine = InferenceEngine(
        endpoint_metas={
            "helloworld": {
                "type": "POST",
                "input_schema": "TextIO",
                "output_schema": "MediaFileIO",
            }
        }
    )

    def hello_world(data: GenericIO) -> TextIO:
        return TextIO(text="hello world!")

    engine._register(
        "helloworld",
        func=hello_world,
        input_schema=GenericIO,
        output_schema=TextIO,
    )
    assert "helloworld" in engine.endpoint_metas
    assert engine.endpoint_metas["helloworld"]["type"] == "POST"
    assert engine.endpoint_metas["helloworld"]["input_schema"] == "GenericIO"
    assert engine.endpoint_metas["helloworld"]["output_schema"] == "TextIO"


def test_register_endpoint():
    engine = InferenceEngine()

    def hello_world(data: GenericIO) -> TextIO:
        return TextIO(text="hello world!")

    engine.entrypoint(
        func=hello_world, input_schema=GenericIO, output_schema=TextIO
    )
    assert "predict" in engine.endpoint_metas
    assert engine.endpoint_metas["predict"]["type"] == "POST"
    assert engine.endpoint_metas["predict"]["input_schema"] == "GenericIO"
    assert engine.endpoint_metas["predict"]["output_schema"] == "TextIO"
