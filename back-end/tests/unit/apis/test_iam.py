from datetime import datetime, timedelta
from typing import Dict, Tuple

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.models.iam import UserInsert

password_strategy = st.from_regex(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$"
)


@pytest.fixture
def userAddData() -> Dict:
    user_data = {
        "user_id": "",
        "name": "Master Tester",
        "password": "Testing123!",
        "password_confirm": "Testing123!",
        "admin_priv": True,
    }

    return user_data


@pytest.fixture
def userConflictData() -> Dict:
    user_data = {
        "user_id": "master1",
        "name": "Master Tester",
        "password": "Testing123!",
        "password_confirm": "Testing123!",
        "admin_priv": True,
    }

    return user_data


@pytest.mark.usefixtures("flush_db")
@pytest.mark.asyncio
@settings(
    suppress_health_check=[
        HealthCheck.filter_too_much,
        HealthCheck.function_scoped_fixture,
    ],
    deadline=timedelta(milliseconds=500),
)
@given(
    st.builds(
        UserInsert,
        password=st.shared(password_strategy, key="password"),
        password_confirm=st.shared(password_strategy, key="password"),
    )
)
async def test_add_users(
    admin_client: TestClient,
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
    user: UserInsert,
):
    db, _ = get_fake_db
    await db.drop_collection("users")
    user_dict = user.dict()
    user_dict["password"] = user.password.get_secret_value()
    user_dict["password_confirm"] = user.password_confirm.get_secret_value()

    response = admin_client.post(
        "/iam/add",
        json=user_dict,
    )
    userList = await db["users"].find().to_list(length=None)
    assert response.status_code == status.HTTP_201_CREATED
    assert len(userList) == 1
    assert userList[0]["name"] == user.name
    assert userList[0]["adminPriv"] == user.admin_priv

    await db.drop_collection("users")


@pytest.mark.xfail(reason="Password mismatch")
@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
@settings(
    suppress_health_check=[
        HealthCheck.filter_too_much,
        HealthCheck.function_scoped_fixture,
    ]
)
@given(
    st.builds(
        UserInsert,
        password=password_strategy,
        password_confirm=password_strategy,
    )
)
async def test_add_users_password_mismatch(
    admin_client: TestClient,
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
    user: UserInsert,
):
    test_add_users(
        admin_client=admin_client,
        get_fake_db=get_fake_db,
        user=user,
    )


@pytest.mark.xfail(reason="Password too weak")
@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
@settings(suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.builds(UserInsert))
async def test_add_users_password_weak(
    admin_client: TestClient,
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
    user: UserInsert,
):
    test_add_users(
        admin_client=admin_client,
        get_fake_db=get_fake_db,
        user=user,
    )


@pytest.mark.usefixtures("flush_db")
@pytest.mark.asyncio
async def test_search_users(
    admin_client: TestClient,
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    await db["users"].insert_one(
        {
            "userId": "searchtest_01",
            "name": "Master Searcher",
            "password": "Testing123!",
            "adminPriv": True,
            "lastModified": str(datetime.now()),
            "created": str(datetime.now()),
        },
    )
    userList = await db["users"].find().to_list(length=None)
    assert len(userList) == 1
    response = admin_client.post(
        "/iam/",
        json={
            "page_num": 1,
            "user_num": 5,
            "name": "",
            "userId": "",
            "admin_priv": 2,
            "last_modified_range": {"from": "", "to": ""},
            "date_created_range": {"from": "", "to": ""},
        },
    )
    content = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert len(content["results"]) == 1
    assert isinstance(content["results"][0], dict)
    assert content["results"][0]["userId"] == "searchtest_01"
    await db.drop_collection("users")


@pytest.mark.usefixtures("flush_db")
@pytest.mark.asyncio
async def test_edit_user(
    admin_client: TestClient,
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    await db["users"].insert_one(
        {
            "userId": "edittest_01",
            "name": "Master Editor",
            "password": "Testing123!",
            "adminPriv": True,
            "lastModified": str(datetime.now()),
            "created": str(datetime.now()),
        },
    )
    userList = await db["users"].find().to_list(length=None)
    assert len(userList) == 1
    response = admin_client.put(
        "/iam/edit",
        json={
            "user_id": "edittest_01",
            "name": "Master Editor Edited",
            "password": "Testing123!",
            "password_confirm": "Testing123!",
            "admin_priv": False,
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    userList = await db["users"].find().to_list(length=None)
    assert len(userList) == 1
    assert userList[0]["name"] == "Master Editor Edited"
    await db.drop_collection("users")


@pytest.mark.usefixtures("flush_db")
@pytest.mark.asyncio
async def test_edit_users_many(
    admin_client: TestClient,
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    await db["users"].insert_many(
        [
            {
                "userId": "edittest_01",
                "name": "Master Editor Many 01",
                "password": "Testing123!",
                "adminPriv": True,
                "lastModified": str(datetime.now()),
                "created": str(datetime.now()),
            },
            {
                "userId": "edittest_02",
                "name": "Master Editor Many 02",
                "password": "Testing123!",
                "adminPriv": True,
                "lastModified": str(datetime.now()),
                "created": str(datetime.now()),
            },
            {
                "userId": "edittest_03",
                "name": "Master Editor Many 03",
                "password": "Testing123!",
                "adminPriv": True,
                "lastModified": str(datetime.now()),
                "created": str(datetime.now()),
            },
        ]
    )
    userList = await db["users"].find().to_list(length=None)
    assert len(userList) == 3
    response = admin_client.put(
        "/iam/edit/multi",
        json={
            "users": ["edittest_01", "edittest_02", "edittest_03"],
            "priv": False,
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    userList = await db["users"].find().to_list(length=None)
    assert len(userList) == 3
    for x in userList:
        assert x["adminPriv"] == False
    await db.drop_collection("users")


@pytest.mark.usefixtures("flush_db")
@pytest.mark.asyncio
async def test_delete_users(
    admin_client: TestClient,
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],
):
    db, _ = get_fake_db
    await db["users"].insert_many(
        [
            {
                "userId": "deltest_01",
                "name": "Master Deleter 01",
                "password": "Testing123!",
                "adminPriv": True,
                "lastModified": str(datetime.now()),
                "created": str(datetime.now()),
            },
            {
                "userId": "deltest_02",
                "name": "Master Deleter 02",
                "password": "Testing123!",
                "adminPriv": True,
                "lastModified": str(datetime.now()),
                "created": str(datetime.now()),
            },
            {
                "userId": "deltest_03",
                "name": "Master Deleter 03",
                "password": "Testing123!",
                "adminPriv": True,
                "lastModified": str(datetime.now()),
                "created": str(datetime.now()),
            },
        ]
    )
    userList = await db["users"].find().to_list(length=None)
    assert len(userList) == 3
    response = admin_client.delete(
        "/iam/delete",
        json={
            "users": ["deltest_03"],
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    userList = await db["users"].find().to_list(length=None)
    assert len(userList) == 2
    response = admin_client.delete(
        "/iam/delete",
        json={
            "users": ["deltest_02", "deltest_01"],
        },
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    userList = await db["users"].find().to_list(length=None)
    assert len(userList) == 0
    await db.drop_collection("users")
