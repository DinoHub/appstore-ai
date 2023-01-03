"""Database Connection to MongoDB"""
from typing import Tuple

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ...config.config import config


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
