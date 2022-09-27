from src.main import app

from fastapi.testclient import TestClient

test_client = TestClient(app)

def test_read_main():
    response = test_client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}