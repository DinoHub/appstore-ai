from motor.motor_asyncio import AsyncIOMotorClient

# TODO: Get MONGODB_URL from config file
MONGODB_URL = "localhost:27017"

mongo_client = AsyncIOMotorClient(MONGODB_URL)

db = mongo_client.app_store
