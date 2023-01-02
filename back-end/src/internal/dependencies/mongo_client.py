"""Database Connection to MongoDB"""
from typing import Tuple
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ...config.config import config
from ..auth import get_password_hash
from ...main import app


# TODO: Use Beanie ORM (https://beanie-odm.dev/) to reduce boilerplate code
def get_db() -> Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]:
    """Get MongoDB connection

    Returns:
        Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]: Connection to MongoDB and Client
    """
    mongo_client = AsyncIOMotorClient(
        config.MONGO_DSN,
        username=config.MONGO_USERNAME,
        password=config.MONGO_PASSWORD,
        authSource=config.DB_NAME,
    )
    db = mongo_client[config.DB_NAME]
    return db, mongo_client


@app.on_event("startup")
def init_db():
    db, _ = get_db()
    db["users"].create_index([("userId", 1)], unique=True)
    db["models"].create_index(
        [("modelId", 1), ("creatorUserId", 1)], unique=True
    )
    db["services"].create_index(
        [("serviceName", 1)], unique=True
    )
    if config.FIRST_SUPERUSER_ID and config.FIRST_SUPERUSER_PASSWORD:
        db["users"].insert_many(
            [  # Create initial root user (admin)
                {
                    "userId": config.FIRST_SUPERUSER_ID,
                    "name": "Root",
                    "password": get_password_hash(config.FIRST_SUPERUSER_PASSWORD),
                    "adminPriv": True,
                    "created" : str(datetime.now()),
                    "lastModified" : str(datetime.now()),
                },
            ]
        )