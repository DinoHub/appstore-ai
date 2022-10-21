import datetime
from typing import Dict, List, Tuple

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.internal.auth import check_is_admin, get_current_user

from .utils import fake_login_admin, fake_login_user, generate_section_model


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
            "model_id": f"test-model-card-{idx}",
            "owner_id": f"test_{idx}",
            "title": f"Test Model {idx}",
            "description": generate_section_model(),
            "limitations": generate_section_model(),
            "metrics": generate_section_model(),
            "explanation": generate_section_model(),
            "deployment": generate_section_model(),
            "performance": generate_section_model(),
            "model_details": generate_section_model(),
            "datetime": str(datetime.datetime.now()),
            "tags": ["Test Tag", f"Tag {idx}"],
            "task": "Testing Model Card",
            "frameworks": ["pytest", f"Framework {idx}"],
            "point_of_contact": "Santa Claus",
            "creator": "Rudolph",
            "inference_engine": {
                "service_url": "http://service_name.namespace.svc.cluster.local",
                "owner_id": f"test_{idx}",
            },
        }
        for idx in range(1, 11)
    ]
    return fake_model_metadata


@pytest.fixture
def clearml_model_metadata() -> Dict:
    return {
        "model_id": f"test-model-card-clearml",
        "title": f"PyTorch MNIST training",
        "description": generate_section_model(),
        "limitations": generate_section_model(),
        "metrics": generate_section_model(),
        "explanation": generate_section_model(),
        "deployment": generate_section_model(),
        "datetime": str(datetime.datetime.now()),
        "tags": ["Test Tag"],
        "task": "Testing Model Card",
        "frameworks": ["pytest"],
        "point_of_contact": "Santa Claus",
        "creator": "Rudolph",
        "inference_engine": {
            "service_url": "http://service_name.namespace.svc.cluster.local",
            "owner_id": "test_1",
        },
        "clearml_exp_id": "e-047f991269004aceaf18a25c3c1def20",
    }
