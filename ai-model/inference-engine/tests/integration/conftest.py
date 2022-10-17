import pytest
from fastapi.testclient import TestClient
from inference_engine.core.engine import InferenceEngine


@pytest.fixture()
def engine() -> InferenceEngine:
    yield InferenceEngine()


@pytest.fixture()
def client(engine: InferenceEngine) -> TestClient:
    client = TestClient(engine.engine)
    return client
