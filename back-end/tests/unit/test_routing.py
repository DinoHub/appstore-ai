import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.parametrize(
    "route,method,expected_status",
    [
        ("/igdg", "GET", status.HTTP_404_NOT_FOUND),
        ("/", "GET", status.HTTP_200_OK),
        # NOTE: below test returns 401 instead of 403 as oauth scheme does not receive auth header
        ("/auth/is_admin", "GET", status.HTTP_401_UNAUTHORIZED),
    ],
)
def test_route_response(
    client: TestClient, route: str, method: str, expected_status: int
):
    response = client.request(method=method, url=route)
    assert response.status_code == expected_status
