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
            "description": "# Markdown Text",
            "performance": "# Markdown Text",
            "created": str(datetime.datetime.now()),
            "lastModified": str(datetime.datetime.now()),
            "tags": ["Test Tag", f"Tag {idx}"],
            "task": "Testing Model Card",
            "frameworks": ["pytest", f"Framework {idx}"],
            "pointOfContact": "Santa Claus",
            "owner": "Rudolph",
            "inferenceApi": "https://fake_inference.com",
            "clearmlExpId": "e-047f991269004aceaf18a25c3c1def20",
        }
        for idx in range(1, 11)
    ]
    return fake_model_metadata


@pytest.fixture
def create_model_card() -> Dict:
    return {
        "title": "Test Model",
        "description": "# Markdown Text",
        "performance": "# Markdown Text",
        "tags": ["Test Tag", "Insert"],
        "task": "Testing Model Card",
        "frameworks": ["pytest"],
        "pointOfContact": "Santa Claus",
        "owner": "Rudolph",
        "inferenceApi": "http://fakeinference.com",
        "clearmlExpId": "e-047f991269004aceaf18a25c3c1def20",
    }
