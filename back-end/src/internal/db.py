"""Database Connection to MongoDB"""
from typing import Tuple

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from ..config.config import config


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


# def init_db():
#     db, _ = get_db()

    # db["users"].create_index([("userId", 1)], unique=True)

    # db["models"].create_index(
    #     [("modelId", 1), ("creatorUserId", 1)], unique=True
    # )
    # db["services"].create_index(
    #     [("serviceName", 1)], unique=True
    # )
    # # TODO: Remove the below code
    # db["users"].insert_many(
    #     [  # Hack to auto insert known user for now
    #         {
    #             "userId": "master",
    #             "name": "Master",
    #             "password": "$2b$12$X86gHxJpDZEc4YHy2oLqU.pwNvvcJP16L5C292q39KuxXmCBW.xdG",
    #             "adminPriv": True,
    #         },
    #         {
    #             "userId": "dev1",
    #             "name": "Developer One",
    #             "password": "$2b$12$coDQnalKv3kw8kzuwztyc.l6gfveM/ERMVQioVYN9OQq6KheDG3ae",
    #             "adminPriv": True,
    #         },
    #     ]
    # )


# init_db()

# Create text index to allow searching
# db["models"].create_index([
#   ( "title" , "text" )
# ], default_language="english")
