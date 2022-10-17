from fastapi.testclient import TestClient
from inference_engine.core.engine import InferenceEngine


def test_status(client: TestClient, engine: InferenceEngine):
    resp = client.get("/")
    resp.raise_for_status()
    resp_json = resp.json()
    assert "metadata" in resp_json
    assert resp_json["metadata"]["name"] == engine.name
    assert resp_json["metadata"]["version"] == engine.version
    assert resp_json["metadata"]["description"] == engine.description
    assert resp_json["metadata"]["author"] == engine.author
    assert resp_json["metadata"]["endpoints"] == engine.endpoint_metas
