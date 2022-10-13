from typing import Tuple

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


def get_db() -> Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]:
    from ..config.config import config

    mongo_client = AsyncIOMotorClient(
        host=config.MONGO_DSN,
        username=config.MONGO_USERNAME,
        password=config.MONGO_PASSWORD,
    )
    db = mongo_client[config.DB_NAME]
    return db, mongo_client


def init_db():
    db, _ = get_db()

    db["users"].create_index([("userid", "text")], unique=True)

    db["models"].create_index([("model_id", "text")], unique=True)


init_db()

# Create text index to allow searching
# db["models"].create_index([
#   ( "title" , "text" )
# ], default_language="english")
