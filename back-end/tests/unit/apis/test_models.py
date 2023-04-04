from datetime import datetime
from random import choice
from typing import Dict, List, Tuple

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.models.model import ModelCardModelIn, UpdateModelCardModel


@pytest.fixture
def model_metadata() -> List[Dict]:
    fake_model_metadata = [
        {
            # "_id": f"test-model-card-{idx}",
            "modelId": f"test-model-card-{idx}",
            "creatorUserId": f"test_{idx}",
            "title": f"Test Model {idx}",
            "markdown": "<h1>Test</h1>",
            "performance": "<h2>Performance</h2>",
            "description": "Lorum ipsum",
            "explanation": "Lorum ipsum",
            "usage": "Lorum ipsum",
            "limitations": "Lorum ipsum",
            "created": str(datetime.now()),
            "lastModified": str(datetime.now()),
            "tags": ["Test Tag", f"Tag {idx}"],
            "task": "Testing Model Card",
            "frameworks": ["pytest", f"Framework {idx}"],
            "pointOfContact": "Santa Claus",
            "owner": "Rudolph",
            "inferenceServiceName": "test-service",
            "experiment": {
                "connector": "clearml",
                "experiment_id": "e-047f991269004aceaf18a25c3c1def20",
            },
            "artifacts": [
                {
                    "artifact_type": "model",
                    "name": "Model Weights",
                    "url": "https://allegro-examples.s3.amazonaws.com/clearml-public-resources/v1.6.4/examples/ClearML%20examples/ML%20%255C%20DL%20Frameworks/Keras/Keras%20with%20TensorBoard%20example.d82abfd682fb4f8cbd12b6bfb5a7c7cf/models/weight.1.hdf5",
                    "timestamp": "2022-10-31T01:57:47.194Z",
                    "framework": "Keras",
                }
            ],
        }
        for idx in range(1, 11)
    ]
    return fake_model_metadata


@pytest.fixture
def create_model_card() -> Dict:
    return {
        "title": "Test Model",
        "markdown": "# Markdown Text",
        "performance": "# Markdown Text",
        "tags": ["Test Tag", "Insert"],
        "task": "Testing Model Card",
        "frameworks": ["pytest"],
        "pointOfContact": "Santa Claus",
        "owner": "Rudolph",
        "inferenceServiceName": "test-service",
        "experiment": {
            "connector": "clearml",
            "experiment_id": "e-047f991269004aceaf18a25c3c1def20",
        },
        "artifacts": [
            {
                "artifact_type": "model",
                "name": "Model Weights",
                "url": "https://allegro-examples.s3.amazonaws.com/clearml-public-resources/v1.6.4/examples/ClearML%20examples/ML%20%255C%20DL%20Frameworks/Keras/Keras%20with%20TensorBoard%20example.d82abfd682fb4f8cbd12b6bfb5a7c7cf/models/weight.1.hdf5",
                "timestamp": "2022-10-31T01:57:47.194Z",
                "framework": "Keras",
            }
        ],
    }


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
    response = client.get("/models", params={"all": True})
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()["results"]) == len(model_metadata)


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
@pytest.mark.parametrize(
    "query,expected_title",
    [
        ({"title": "Test Model 1"}, "Test Model 1"),
        ({"tags[]": ["Test Tag", "Tag 2"]}, "Test Model 2"),
        ({"creator": "test_4"}, "Test Model 4"),
        ({"frameworks[]": ["Framework 3"]}, "Test Model 3"),
        ({"sort_by": "lastModified", "desc": True}, "Test Model 10"),
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
    response = client.get("/models", params=query)
    response_json = response.json()
    assert response.status_code == status.HTTP_200_OK
    assert len(response_json["results"]) != 0
    assert (
        response_json["results"][0]["title"] == expected_title
    ), "Wrong card retrieved"


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
    model_card_id = model_metadata[0]["modelId"]
    creator_user_id = model_metadata[0]["creatorUserId"]
    response = client.get(f"/models/{creator_user_id}/{model_card_id}")
    assert response.status_code == status.HTTP_200_OK

# NOTE: Disable this test for now until a solution to simulate or create a K8S cluster specifically for pytests is created
# @pytest.mark.usefixtures("flush_db")
# def test_create_model_card_metadata(
#     client: TestClient,
#     create_model_card: Dict,
# ):
#     response = client.post("/models/", json=create_model_card)
#     assert response.status_code == status.HTTP_201_CREATED

#     result = response.json()
#     assert result["title"] == create_model_card["title"]

# NOTE: Disable this test for now until a solution to simulate or create a K8S cluster specifically for pytests is created
# @pytest.mark.usefixtures("flush_db")
# @given(st.builds(ModelCardModelIn))
# def test_create_model_card_metadata_hypothesis(
#     client: TestClient,
#     model_card: ModelCardModelIn,
# ):
#     response = client.post("/models/", json=model_card.dict())
#     assert response.status_code == status.HTTP_201_CREATED

#     result = response.json()
#     for key, value in model_card.dict().items():
#         print(key, value)
#         # skip markdown and performance til we can generate html
#         if value is not None:
#             if key in ("markdown", "performance"):
#                 continue
#             if key in ("tags", "frameworks"):
#                 assert set(result[key]) == set(value)
#             else:
#                 assert result[key] == value


@pytest.mark.asyncio
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.builds(UpdateModelCardModel))
async def test_update_model_card_metadata(
    client: TestClient,
    model_metadata: List[Dict],
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
    update_model_card: UpdateModelCardModel,
):
    db, _ = get_fake_db
    # Manually flush as fixture will only run once
    # when using hypothesis
    for collection in await db.list_collection_names():
        await db.drop_collection(collection)
    for obj in model_metadata:
        await db["models"].insert_one(obj)

    # Check length before anything
    assert len((await db["models"].find().to_list(length=None))) == len(
        model_metadata
    )

    # Get model ID
    # Pick a random model card
    card = choice(await db["models"].find().to_list(length=1))
    model_card_id = str(card["modelId"])
    creator_user_id = str(card["creatorUserId"])

    # Updated Sections
    update = update_model_card.dict(exclude_none=True)

    response = client.put(
        f"/models/{creator_user_id}/{model_card_id}", json=update
    )
    print(response.text)
    assert response.status_code == status.HTTP_200_OK

    # Check that updates took place
    # Find all model cards, check they are the same
    # except for the one we updated
    models = await db["models"].find().to_list(length=None)
    assert len(models) == len(model_metadata)
    # Create a dict mapping userId/modelId to model
    model_map = {
        model["creatorUserId"] + "/" + model["modelId"]: model
        for model in model_metadata
    }
    for model in models:
        if model["modelId"] == model_card_id:
            for key, value in model.items():
                if key in update:
                    assert value == update[key]
                else:
                    assert (
                        value
                        == model_map[
                            model["creatorUserId"] + "/" + model["modelId"]
                        ][key]
                    )
        else:
            # Compare to original
            assert (
                model
                == model_map[model["creatorUserId"] + "/" + model["modelId"]]
            )


@pytest.mark.usefixtures("flush_db")
def test_update_model_card_not_found(
    client: TestClient,
):
    response = client.put(
        f"/models/test_1/invalid_id", json={"title": "Hello"}
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

# NOTE: Disable this test for now until a solution to simulate or create a K8S cluster specifically for pytests is created
# @pytest.mark.asyncio
# @pytest.mark.usefixtures("flush_db")
# async def test_delete_model_card_metadata(
#     client: TestClient,
#     model_metadata: List[Dict],
#     get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
# ):
#     db, _ = get_fake_db
#     await db["models"].insert_one(model_metadata[0])
#     # Check length before anything
#     assert len((await db["models"].find().to_list(length=None))) == 1

#     # Get model ID
#     card = (await db["models"].find().to_list(length=1))[0]
#     model_card_id = str(card["modelId"])
#     creator_user_id = str(card["creatorUserId"])

#     # Send delete request
#     response = client.delete(
#         f"/models/{creator_user_id}/{model_card_id}",
#     )
#     assert response.status_code == status.HTTP_204_NO_CONTENT

#     # Check that database has actually been emptied
#     assert len((await db["models"].find().to_list(length=None))) == 0


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_delete_model_card_metadata_unauthorized(
    client: TestClient,
    model_metadata: List[Dict],
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    card = model_metadata[0]
    card["creatorUserId"] = "other_user"
    await db["models"].insert_one(card)
    # Check length before anything
    assert len((await db["models"].find().to_list(length=None))) == 1
    # Get model ID
    card = (await db["models"].find().to_list(length=1))[0]
    model_card_id = str(card["modelId"])
    creator_user_id = str(card["creatorUserId"])
    # Send delete request
    response = client.delete(
        f"/models/{creator_user_id}/{model_card_id}",
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

    # Check that database is unaffected
    assert len((await db["models"].find().to_list(length=None))) == 1
