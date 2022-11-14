import datetime
from typing import Dict, List, Tuple

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.internal.auth import check_is_admin, get_current_user

from .utils import fake_login_admin, fake_login_user


@pytest.fixture
def client() -> TestClient:
    from src.config import config

    config.ENV_STATE = "test"
    config.config = config.TestingConfig()
    from src.main import app

    app.dependency_overrides[get_current_user] = fake_login_user
    if check_is_admin in app.dependency_overrides:
        del app.dependency_overrides[check_is_admin]
    client = TestClient(app)
    return client


@pytest.fixture
def admin_client(client: TestClient) -> TestClient:
    from src.config import config

    config.ENV_STATE = "test"
    config.config = config.TestingConfig()
    from src.main import app

    app.dependency_overrides[get_current_user] = fake_login_user
    app.dependency_overrides[check_is_admin] = fake_login_admin
    client = TestClient(app)
    return client


@pytest.fixture
def anonymous_client(client: TestClient) -> TestClient:
    from src.config import config

    config.ENV_STATE = "test"
    config.config = config.TestingConfig()
    from src.main import app

    if check_is_admin in app.dependency_overrides:
        del app.dependency_overrides[check_is_admin]
    if get_current_user in app.dependency_overrides:
        del app.dependency_overrides[get_current_user]
    client = TestClient(app)
    return client


@pytest.fixture()
def get_fake_db(client) -> Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]:
    from src.internal.db import get_db

    db, client = get_db()
    return db, client


@pytest_asyncio.fixture
async def flush_db(
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]
):
    db, client = get_fake_db
    for collection in await db.list_collection_names():
        await db.drop_collection(collection)


@pytest.fixture
def model_metadata() -> List[Dict]:
    fake_model_metadata = [
        {
            "modelId": f"test-model-card-{idx}",
            "creatorUserId": f"test_{idx}",
            "title": f"Test Model {idx}",
            "markdown": "<h1>Test</h1>",
            "performance": "<h2>Performance</h2>",
            "description": "Lorum ipsum",
            "explanation": "Lorum ipsum",
            "usage": "Lorum ipsum",
            "limitations": "Lorum ipsum",
            "created": str(datetime.datetime.now()),
            "lastModified": str(datetime.datetime.now()),
            "tags": ["Test Tag", f"Tag {idx}"],
            "task": "Testing Model Card",
            "frameworks": ["pytest", f"Framework {idx}"],
            "pointOfContact": "Santa Claus",
            "owner": "Rudolph",
            "inferenceServiceName": "test-service",
            "clearmlExpId": "e-047f991269004aceaf18a25c3c1def20",
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
        "clearmlExpId": "e-047f991269004aceaf18a25c3c1def20",
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
