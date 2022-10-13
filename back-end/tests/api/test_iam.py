from typing import Dict, List, Tuple

import pytest
from bson import ObjectId
from fastapi import status
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_login(
    client: TestClient,
    temp_user: Dict,
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):  
    
    db, _ = get_fake_db
    message = await db["users"].insert_one(temp_user)
    print(message)
    response = client.post("/models/search", json={})
    assert response.status_code == status.HTTP_200_OK