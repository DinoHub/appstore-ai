from typing import Tuple

import pytest
import pytest_asyncio
from fastapi import FastAPI
from fastapi.testclient import TestClient
from miniopy_async import Minio
from miniopy_async.deleteobjects import DeleteObject
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.internal.auth import check_is_admin, get_current_user
from src.main import app as fastapi_app

from .utils import fake_login_admin, fake_login_user


@pytest.fixture(scope="module")
def application() -> FastAPI:
    fastapi_app.app.dependency_overrides[get_current_user] = fake_login_user
    if check_is_admin in fastapi_app.app.dependency_overrides:
        del fastapi_app.app.dependency_overrides[check_is_admin]
    return fastapi_app.app


@pytest.fixture(scope="module")
def client(application) -> TestClient:
    return TestClient(application)


@pytest.fixture
def admin_client(client: TestClient) -> TestClient:
    fastapi_app.app.dependency_overrides[get_current_user] = fake_login_user
    fastapi_app.app.dependency_overrides[check_is_admin] = fake_login_admin
    client = TestClient(fastapi_app.app)
    return client


@pytest.fixture
def anonymous_client(client: TestClient) -> TestClient:
    if check_is_admin in fastapi_app.dependency_overrides:
        del fastapi_app.app.dependency_overrides[check_is_admin]
    if get_current_user in fastapi_app.dependency_overrides:
        del fastapi_app.app.dependency_overrides[get_current_user]
    client = TestClient(fastapi_app)
    return client


@pytest.fixture
def get_fake_db(client) -> Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]:
    from src.internal.dependencies.mongo_client import get_db

    db, db_client = get_db()
    return db, db_client


@pytest_asyncio.fixture
async def flush_db(get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]):
    db, client = get_fake_db
    for collection in await db.list_collection_names():
        await db.drop_collection(collection)


@pytest_asyncio.fixture
async def s3_client(client: TestClient) -> Minio:
    from src.internal.dependencies.minio_client import minio_api_client

    s3_client = await minio_api_client()
    return s3_client


@pytest_asyncio.fixture
async def flush_s3(s3_client: Minio):
    from src.config.config import config

    objects = await s3_client.list_objects(config.MINIO_BUCKET_NAME, recursive=True)
    objects_to_delete = map(lambda x: DeleteObject(x.object_name), objects)
    results = await s3_client.remove_objects(
        config.MINIO_BUCKET_NAME, objects_to_delete
    )
    for result in results:
        pass
