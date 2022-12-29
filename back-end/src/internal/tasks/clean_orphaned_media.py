from typing import Set, List

from bs4 import BeautifulSoup
from minio.deleteobjects import DeleteObject

from ...config.config import config
from ..db import get_db
from ..minio_client import minio_api_client

async def delete_orphan_images():
    print("INFO: Starting task to remove orphaned images")
    db, _ = get_db()
    s3_client = minio_api_client()
    bucket_name = config.MINIO_BUCKET_NAME

    # Find all existing images
    if s3_client is None or bucket_name is None:
        print("WARN: Unable to get s3 client or bucket_name is None. Returning.")
        return

    objects = list(s3_client.list_objects(
        bucket_name,
        "images/"
    ))
    object_names: Set[str] = set([
         obj.object_name for obj in objects
    ])
    print(f"INFO: There are {len(object_names)} objects currently stored.")

    # Get all markup
    model_cards: List[dict] = await (
        db["models"].find(
            {}, {"markdown" : 1, "performance" : 1}
        )
    ).to_list(length=None)

    # From markdown and performance, extract all image tags
    image_sources: Set[str] = set()
    prefix = f"{config.MINIO_API_HOST}/{bucket_name}/"

    for card in model_cards:
        for field in ("markdown", "performance"):
            parser = BeautifulSoup(card[field], "lxml")
            images = parser.find_all("img")
            for image in images:
                source: str = image["src"]
                if not source.startswith(prefix):
                    continue
                image_sources.add(source.removeprefix(
                    prefix
                ))
    
    # Do a set difference to get orphaned objects
    print(f"Image sources: {image_sources}")
    print(f"Inside Minio: {object_names}")
    print(f"INFO: There are {len(image_sources)} images found in the model cards.")
    orphaned_images = object_names.difference(image_sources)
    print(f"INFO: There are {len(orphaned_images)} orphaned images to be removed.")

    # Remove orphaned images
    errors = list(s3_client.remove_objects(
        bucket_name,
        [DeleteObject(
            name
        ) for name in orphaned_images]
    ))
    print(f"INFO: Number of errors: {len(errors)} in deletion.")
    for error in errors:
        print(f"ERROR: {error}")
    print("INFO: Task Complete (Deleted orphaned task)")




