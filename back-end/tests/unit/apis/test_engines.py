# TODO: Mock K8S API Calls to allow testing of inference engine endpoints
# NOTE: Currently no mock clients exist yet
# https://github.com/kubernetes-client/python/issues/524
# So for now, probably only feasible to use integration testing
# with actual k3s/kind cluster
from datetime import datetime
from typing import Dict, List, Tuple

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


@pytest.fixture
def service_metadata() -> List[Dict]:
    return [
        {
            "inferenceUrl": f"http://localhost-{i}:8080",
            "ownerId": f"test-{i}",
            "serviceName": f"test-{i}",
            "created": str(datetime.now()),
            "lastModified": str(datetime.now()),
            "modelId": f"test-{i}",
            "imageUri": f"dev.local/test:1.0",
            "host": "localhost-{i}",
            "path": "",
            "backend": "emissary",
        }
        for i in range(5)
    ]


# NOTE: Disable this test for now until a solution to simulate or create a K8S cluster specifically for pytests is created
# @pytest.mark.asyncio
# @pytest.mark.usefixtures("flush_db")
# async def test_get_inference_engine_service(
#     client: TestClient,
#     service_metadata: List[Dict],
#     get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
# ):
#     db, _ = get_fake_db

#     for service in service_metadata:
#         await db["services"].insert_one(service)

#     # Check that has been inserted
#     assert len((await db["services"].find().to_list(length=None))) == 5

#     for service in service_metadata:
#         response = client.get(f"/engines/{service['serviceName']}")
#         assert response.status_code == status.HTTP_200_OK
