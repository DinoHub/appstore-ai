from typing import Tuple

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


def get_db() -> Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient]:
    from ..config.config import config
    if config.ENV_STATE == "test":
        # Using Fake Database for Testing
        print("Use mock database")
        mongo_client = mongomock_motor.AsyncMongoMockClient() 
    else:
        mongo_client = AsyncIOMotorClient(config.MONGODB_URL)
    db = mongo_client[config.MAIN_COLLECTION_NAME]
    return db, mongo_client


# Create text index to allow searching
# db["models"].create_index([
#   ( "title" , "text" )
# ], default_language="english")
