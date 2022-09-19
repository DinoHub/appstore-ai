from os import device_encoding
from motor.motor_asyncio import AsyncIOMotorClient

from config.config import config

mongo_client = AsyncIOMotorClient(config.MONGODB_URL)

db = mongo_client.app_store

# Create text index to allow searching
# db["models"].create_index([
#   ( "title" , "text" )
# ], default_language="english")
