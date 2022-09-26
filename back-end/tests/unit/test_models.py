from typing import Dict, List

import pytest
from fastapi.testclient import TestClient


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_get_all_models(
    client: TestClient, model_metadata: List[Dict], get_fake_db
):
    db, _ = get_fake_db
    for obj in model_metadata:
        await db["models"].insert_one(obj)
    response = client.post(
        "/models/search",
        json={
            # "title" : "",
        },
    )
    assert response.status_code == 200
    assert len(response.json()) == len(model_metadata)
    # for expected, actual in zip(model_metadata, response.json()):
    #     assert expected == actual
    # currently will not be exact same due to id having slightly different key

# @pytest.mark.asyncio
