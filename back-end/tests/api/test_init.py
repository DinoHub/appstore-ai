from fastapi.testclient import TestClient


def test_hello_world(client: TestClient):
    """Test that main app is able to load."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World"}
