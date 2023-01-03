"""Initialize MongoDB database with default data and index."""
from datetime import datetime

from ...config.config import config
from ..auth import get_password_hash
from ..dependencies.mongo_client import get_db


def init_db():
    """Initialize MongoDB database with default data and index."""
    db, _ = get_db()
    db["users"].create_index([("userId", 1)], unique=True)
    db["models"].create_index(
        [("modelId", 1), ("creatorUserId", 1)], unique=True
    )
    db["services"].create_index([("serviceName", 1)], unique=True)
    if config.FIRST_SUPERUSER_ID and config.FIRST_SUPERUSER_PASSWORD:
        print("Creating root user...")
        db["users"].insert_many(
            [  # Create initial root user (admin)
                {
                    "userId": config.FIRST_SUPERUSER_ID,
                    "name": "Root",
                    "password": get_password_hash(
                        config.FIRST_SUPERUSER_PASSWORD
                    ),
                    "adminPriv": True,
                    "created": str(datetime.now()),
                    "lastModified": str(datetime.now()),
                },
            ]
        )
    else:
        print("No root user created.")
