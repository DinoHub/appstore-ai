from pathlib import Path
from typing import Dict, List, Tuple

import pytest
from fastapi.testclient import TestClient
from miniopy_async import Minio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from aiohttp import client_reqrep

from .test_models import model_metadata
from src.config.config import config

BUCKET_NAME = config.MINIO_BUCKET_NAME


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_s3")
@pytest.mark.parametrize("file_path", ["./test_data/video1.mp4"])
async def test_upload_video(file_path: str, client: TestClient, s3_client: Minio):
    # Check that s3 is empty at start
    objects = await s3_client.list_objects(BUCKET_NAME, recursive=True)  # type: ignore #ignore
    assert len(objects) == 0  # type: ignore #ignore
    response = client.post(
        "/buckets/video",
        files={"video": open(Path(__file__).parent.joinpath(file_path), "rb")},
    )
    data = response.json()
    response.raise_for_status()
    assert "video_location" in data

    video_location: str = data["video_location"]
    bucket, object_name = video_location.removeprefix("s3://").split("/", maxsplit=1)
    assert bucket == BUCKET_NAME

    # Check that path exists
    s3_response: client_reqrep.ClientResponse = await s3_client.get_object(
        BUCKET_NAME, object_name
    )
    assert s3_response.status != 404
    s3_response.close()
    await s3_response.release()


@pytest.mark.asyncio
@pytest.mark.usefixtures("flush_s3", "flush_db")
@pytest.mark.parametrize(
    "old_file,new_file", [("./test_data/video1.mp4", "./test_data/video2.mp4")]
)
async def test_update_video(
    old_file: str,
    new_file: str,
    client: TestClient,
    s3_client: Minio,
    get_fake_db: Tuple[AsyncIOMotorDatabase, AsyncIOMotorClient],  # type: ignore #ignore
    model_metadata: List[Dict],
):
    db, _ = get_fake_db
    await test_upload_video(old_file, client, s3_client)

    # Check that file exists
    objects = await s3_client.list_objects(BUCKET_NAME, recursive=True)
    old_object_name = objects[0].object_name  # type: ignore #ignore
    assert len(objects) == 1  # type: ignore #ignore

    # Create a model card containing the old video
    card = model_metadata[0]
    del card["inferenceServiceName"]
    card["videoLocation"] = f"s3://{BUCKET_NAME}/{old_object_name}"

    await db["models"].insert_one(card)

    # Now attempt to replace
    response = client.put(
        "/buckets/video",
        data={"userId": card["creatorUserId"], "modelId": card["modelId"]},
        files={"new_video": open(Path(__file__).parent.joinpath(new_file), "rb")},
    )
    response.raise_for_status()
    data = response.json()
    assert "video_location" in data

    # Then check whether it has been replaced
    objects = await s3_client.list_objects(BUCKET_NAME, recursive=True)  # type: ignore #ignore
    assert len(objects) == 1  # type: ignore #ignore
    new_object_name = objects[0].object_name  # type: ignore #ignore
    assert old_object_name != new_object_name
