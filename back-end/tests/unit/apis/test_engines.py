# TODO: Mock K8S API Calls to allow testing of inference engine endpoints
from datetime import datetime
from typing import Dict, List, Tuple

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

@pytest.fixture
def service_metadata() -> List[Dict]:
    return [{
        "inference_url" : f"http://localhost-{i}:8080",
        "owner_id" : f"test-{i}",
        "service_name" : f"test-{i}",
        "created" : str(datetime.now()),
        "last_modified" : str(datetime.now()),
    }
    for i in range(5)]

@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_get_inference_engine_service(
    client: TestClient,
    service_metadata: List[Dict],
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db

    for service in service_metadata:
        await db.services.insert_one(service)

    for service in service_metadata:
        response = client.get(f"/engines/{service['service_name']}")
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == service