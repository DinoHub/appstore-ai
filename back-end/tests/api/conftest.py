import datetime
from typing import Dict, List, Tuple

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.models.dataset import DatasetModel

from .utils.fake_db import generate_section_model


@pytest.fixture(scope="session")
def client() -> TestClient:
    from src.config import config

    config.ENV_STATE = "test"
    assert config.ENV_STATE == "test"
    config.config = config.TestingConfig()
    config.config.set_envvar()
    assert isinstance(config.config, config.TestingConfig)
    from src.main import app

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
            "owner": f"Santa Claus {idx}",
            "creator": "Rudolph",
            "inference_engine": {
                "image_uri": "hub/inference_image:latest",
                "name": "ie-inference-engine",
                "input_schema": {
                    "io_type": "GenericIO",
                    "json_schema": {
                        "media": {"type": "media"},
                        "parameters": {"type": "json", "required": False},
                    },
                },
                "output_schema": {"io_type": "TextIO"},
            },
        }
        for idx in range(1, 11)
    ]
    return fake_model_metadata
