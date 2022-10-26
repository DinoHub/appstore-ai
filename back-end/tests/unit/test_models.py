from typing import Dict, List, Tuple

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_get_all_models(
    client: TestClient,
    model_metadata: List[Dict],
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    for obj in model_metadata:
        await db["models"].insert_one(obj)
    response = client.post("/models/search", json={})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == len(model_metadata)
    # for expected, actual in zip(model_metadata, response.json()):
    #     assert expected == actual
    # currently will not be exact same due to id having slightly different key


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
@pytest.mark.parametrize(
    "query,expected_title",
    [
        ({"title": "Test Model 1"}, "Test Model 1"),
        ({"tags": ["Test Tag", "Tag 2"]}, "Test Model 2"),
        ({"creator_user_id": "test_4"}, "Test Model 4"),
        ({"frameworks": ["Framework 1"]}, "Test Model 1"),
    ],
)
async def test_search_models(
    query: Dict,
    expected_title: str,
    client: TestClient,
    model_metadata: List[Dict],
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    for obj in model_metadata:
        await db["models"].insert_one(obj)

    # Send request
    response = client.post("/models/search", json=query)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json) != 0
    assert response_json[0]["title"] == expected_title, "Wrong card retrieved"


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_get_model_card_by_id(
    client: TestClient,
    model_metadata: List[Dict],
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    # Insert model card first
    db, _ = get_fake_db
    await db["models"].insert_one(model_metadata[0])
    # Get id
    model_card_id = str(
        (await db["models"].find().to_list(length=1))[0]["model_id"]
    )
    response = client.get(f"/models/{model_card_id}")
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.usefixtures("flush_db")
def test_create_model_card_metadata(
    client: TestClient,
    model_metadata: List[Dict],
):
    for metadata in model_metadata:
        del metadata["creator_user_id"]
        del metadata["model_id"]
        response = client.post("/models/", json=metadata)
        assert response.status_code == status.HTTP_201_CREATED

        result = response.json()
        assert result["title"] == metadata["title"]


@pytest.mark.parametrize("card", [{"title": "hello world"}])
@pytest.mark.xfail(reason="Invalid Input")
@pytest.mark.usefixtures("flush_db")
def test_create_model_card_invalid_expid(card: Dict):
    test_create_model_card_metadata(model_metadata=[card])


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_update_model_card_metadata(
    client: TestClient,
    model_metadata: List[Dict],
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    await db["models"].insert_one(model_metadata[0])
    # Check length before anything
    assert len((await db["models"].find().to_list(length=None))) == 1

    # Get model ID
    model_card_id = str(
        (await db["models"].find().to_list(length=1))[0]["model_id"]
    )

    # Updated Sections
    update = {
        "title": "Updated Title",
    }

    response = client.put(f"/models/{model_card_id}", json=update)

    assert response.status_code == status.HTTP_200_OK

    # Check that updates took place
    model = await db["models"].find_one({"model_id": model_card_id})
    assert model is not None
    assert model["title"] == update["title"]


@pytest.mark.usefixtures("flush_db")
def test_update_model_card_not_found(
    client: TestClient,
):
    response = client.put(f"/models/invalid_id", json={"title": "Hello"})
    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_delete_model_card_metadata(
    client: TestClient,
    model_metadata: List[Dict],
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    await db["models"].insert_one(model_metadata[0])
    # Check length before anything
    assert len((await db["models"].find().to_list(length=None))) == 1

    # Get model ID
    model_card_id = str(
        (await db["models"].find().to_list(length=1))[0]["model_id"]
    )

    # Send delete request
    response = client.delete(
        f"/models/{model_card_id}",
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT

    # Check that database has actually been emptied
    assert len((await db["models"].find().to_list(length=None))) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_delete_model_card_metadata_unauthorized(
    client: TestClient,
    model_metadata: List[Dict],
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    card = model_metadata[0]
    card["creator_user_id"] = "other_user"
    await db["models"].insert_one(card)
    # Check length before anything
    assert len((await db["models"].find().to_list(length=None))) == 1

    # Get model ID
    model_card_id = str(
        (await db["models"].find().to_list(length=1))[0]["model_id"]
    )

    # Send delete request
    response = client.delete(
        f"/models/{model_card_id}",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Check that database is unaffected
    assert len((await db["models"].find().to_list(length=None))) == 1
