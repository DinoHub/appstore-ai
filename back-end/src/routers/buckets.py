"""Endpoints for handling object storage buckets."""
import uuid
from typing import Dict

from colorama import Fore
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from miniopy_async import Minio

from ..config.config import config
from ..internal.dependencies.file_validator import ValidateFileUpload
from ..internal.dependencies.minio_client import (
    minio_api_client,
    remove_data,
    upload_data,
)
from ..internal.dependencies.mongo_client import get_db
from ..models.buckets import VideoUploadResponse

router = APIRouter(prefix="/buckets", tags=["Buckets"])

BUCKET_NAME = config.MINIO_BUCKET_NAME or "default"

MAX_UPLOAD_SIZE_MB = 10
BYTES_PER_MB = 1000000
video_validator = ValidateFileUpload(
    max_upload_size=int(BYTES_PER_MB * MAX_UPLOAD_SIZE_MB),
    accepted_content_types=[
        "video/mp4",
        "video/avi",
        "video/mov",
        "video/mkv",
        "video/webm",
    ],
)


@router.post(
    "/video",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(video_validator)],
    response_model=VideoUploadResponse,
)
async def upload_video(
    video: UploadFile = Form(),
    s3_client: Minio = Depends(minio_api_client),
) -> Dict[str, str]:
    """Uploads a video to the MinIO bucket

    Args:
        video (UploadFile): Video file to upload
        s3_client (Minio, optional): Minio client. Defaults to Depends(minio_api_client).

    Raises:
        HTTPException: 500 if something went wrong

    Returns:
        Dict[str, str]: Location of the video in the bucket
    """
    try:
        path = await upload_data(
            s3_client,
            video.file.read(),
            f"videos/{uuid.uuid4().hex}.{video.content_type.replace('video/','')}",
            BUCKET_NAME,
            video.content_type,
        )
        return {"video_location": path}
    except Exception as err:
        print(f"{Fore.RED}ERROR{Fore.WHITE}:\t  {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong the upload",
        ) from err


@router.put(
    "/video",
    status_code=status.HTTP_200_OK,
    # dependencies=[Depends(video_validator)],
    response_model=VideoUploadResponse,
)
async def replace_video(
    new_video: UploadFile = Form(),
    userId: str = Form(),
    modelId: str = Form(),
    s3_client: Minio = Depends(minio_api_client),
    db=Depends(get_db),
) -> Dict[str, str]:
    """Replaces the video of a model

    Args:
        new_video (UploadFile): New video to upload. Defaults to Form().
        userId (str, optional): userId of model card. Defaults to Form().
        modelId (str, optional): modelId of model card. Defaults to Form().
        s3_client (Minio, optional): Connection to S3 storage. Defaults to Depends(minio_api_client).
        db (_type_, optional): Connection to MongoDB. Defaults to Depends(get_db).

    Raises:
        HTTPException: 500 if something went wrong

    Returns:
        Dict[str, str]: A dictionary with the location of the new video in the bucket
    """
    try:
        # remove the old video inside the bucket
        db, mongo_client = db

        async with await mongo_client.start_session() as session:
            async with session.start_transaction():
                existing_card = await db["models"].find_one(
                    {
                        "modelId": modelId,
                        "creatorUserId": userId,
                    }
                )
                try:
                    url: str = existing_card["videoLocation"]
                    url = url.removeprefix("s3://")
                    bucket, object_name = url.split("/", 1)
                    await remove_data(s3_client, object_name, bucket)
                except Exception as err:
                    print(f"{Fore.RED}ERROR{Fore.WHITE}:\t  {err}")
                    print("WARN:\t  No old video location provided")
        # upload the new video to the bucket
        path = await upload_data(
            s3_client,
            new_video.file.read(),
            f"videos/{uuid.uuid4().hex}.{new_video.content_type.replace('video/','')}",
            BUCKET_NAME,
            new_video.content_type,
        )
        return {"video_location": path}
    except Exception as err:
        print(f"{Fore.RED}ERROR{Fore.WHITE}:\t  {err}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong with the upload",
        ) from err
