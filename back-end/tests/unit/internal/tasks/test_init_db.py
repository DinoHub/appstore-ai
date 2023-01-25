from typing import Tuple

import pytest

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from src.internal.tasks import init_db
from src.internal.auth import verify_password
from src.config.config import config

@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_db")
async def test_init_db(
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]
):  
    db_conn, _ = get_fake_db
    first_superuser_id = config.FIRST_SUPERUSER_ID
    first_superuser_pass = config.FIRST_SUPERUSER_PASSWORD

    await init_db()
    user = await db_conn["users"].find_one({
        "userId" : first_superuser_id
    })
    assert user is not None
    assert verify_password(first_superuser_pass, user["password"])



