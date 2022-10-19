from fastapi.testclient import TestClient


def test_read_users(admin_client: TestClient):
    response = admin_client.post("/iam/1", json=dict(user_num=5, admin_priv=1))
    assert response.status_code == 200
