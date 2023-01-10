import datetime
from typing import Dict, List, Tuple

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.config.config import Environment
from src.internal.auth import check_is_admin, get_current_user

from .utils import fake_login_admin, fake_login_user


@pytest.fixture
def app() -> FastAPI:
    from src.config import config

    config.ENV_STATE = Environment.TEST
    config.config = config.TestingConfig(ENV_STATE=Environment.TEST)
    from src.main import app as fastapi_app

    fastapi_app.app.dependency_overrides[get_current_user] = fake_login_user
    if check_is_admin in fastapi_app.app.dependency_overrides:
        del fastapi_app.app.dependency_overrides[check_is_admin]
    return fastapi_app.app


@pytest.fixture
def client(app) -> TestClient:
    # from src.config import config

    # config.ENV_STATE = "test"
    # config.config = config.TestingConfig()
    # from src.main import app

    # app.dependency_overrides[get_current_user] = fake_login_user
    # if check_is_admin in app.dependency_overrides:
    #     del app.dependency_overrides[check_is_admin]
    return TestClient(app)


@pytest.fixture
def admin_client(client: TestClient) -> TestClient:
    from src.config import config

    config.ENV_STATE = Environment.TEST
    config.config = config.TestingConfig()
    from src.main import fastapi_app

    fastapi_app.dependency_overrides[get_current_user] = fake_login_user
    fastapi_app.dependency_overrides[check_is_admin] = fake_login_admin
    client = TestClient(fastapi_app)
    return client


@pytest.fixture
def anonymous_client(client: TestClient) -> TestClient:
    from src.config import config

    config.ENV_STATE = "test"
    config.config = config.TestingConfig()
    from src.main import fastapi_app

    if check_is_admin in fastapi_app.dependency_overrides:
        del fastapi_app.dependency_overrides[check_is_admin]
    if get_current_user in fastapi_app.dependency_overrides:
        del fastapi_app.dependency_overrides[get_current_user]
    client = TestClient(fastapi_app)
    return client


@pytest.fixture()
def get_fake_db(client) -> Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]:
    from src.internal.dependencies.mongo_client import get_db

    db, db_client = get_db()
    return db, db_client


@pytest_asyncio.fixture
async def flush_db(
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]
):
    db, client = get_fake_db
    for collection in await db.list_collection_names():
        await db.drop_collection(collection)
