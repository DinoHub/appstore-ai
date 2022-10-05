from typing import Tuple

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


def get_db() -> Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]:
    from ..config.config import config
    mongo_client = AsyncIOMotorClient(host = config.MONGODB_URL,username =config.MONGO_USERNAME,password=config.MONGO_PASSWORD )
    db = mongo_client[config.MAIN_COLLECTION_NAME]
    return db, mongo_client


# Create text index to allow searching
# db["models"].create_index([
#   ( "title" , "text" )
# ], default_language="english")
