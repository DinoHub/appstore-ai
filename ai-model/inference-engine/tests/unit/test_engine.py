from pathlib import Path
from typing import Dict

from inference_engine.core.engine import InferenceEngine
from yaml import safe_load


def test_create_engine():
    engine = InferenceEngine()


def test_create_engine_from_dict():
    config = {
        "name": "Test 1",
        "version": "v9",
        "description": "Hello World!",
    }

    engine = InferenceEngine.from_dict(config)
    for key, value in config.items():
        assert getattr(engine, key) == value


def test_create_engine_from_yaml():
    path = str(
        Path(__file__).parent.parent.joinpath("data", "meta.yml").absolute()
    )
    engine = InferenceEngine.from_yaml(path)
    config: Dict = safe_load(open(path, "r"))
    for key, value in config.items():
        assert getattr(engine, key) == value
