from fastapi.testclient import TestClient

from src.main import app

test_client = TestClient(app)


def test_read_main():
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
