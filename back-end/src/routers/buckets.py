"""Endpoints for handling object storage buckets."""
import uuid
from typing import Dict, Optional

from colorama import Fore
from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from minio import Minio

from ..config.config import config
from ..internal.dependencies.file_validator import ValidateFileUpload
from ..internal.dependencies.minio_client import (
    minio_api_client,
    remove_data,
    upload_data,
)
from ..models.buckets import VideoUploadResponse

router = APIRouter(prefix="/buckets", tags=["buckets"])

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
def upload_video(
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
        path = upload_data(
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
def replace_video(
    new_video: UploadFile = Form(),
    old_video_location: Optional[str] = Form(None),
    s3_client: Minio = Depends(minio_api_client),
) -> Dict[str, str]:
    """Replaces a video in the MinIO bucket

    Args:
        new_video (UploadFile, optional): New video. Defaults to Form().
        old_video_location (Optional[str], optional): Location of video to replace.
            Defaults to Form(None).
        s3_client (Minio, optional): Minio client. Defaults to Depends(minio_api_client).

    Raises:
        HTTPException: 500 if something went wrong

    Returns:
        Dict[str, str]: Location of the new video in the bucket
    """
    try:
        # remove the old video inside the bucket
        if old_video_location is not None:
            video_location = old_video_location.replace(
                f"{config.MINIO_API_HOST}/{config.MINIO_BUCKET_NAME}/", ""
            )
            remove_data(s3_client, video_location, config.MINIO_BUCKET_NAME)
        else:
            print("WARN:\t  No old video location provided")

        # upload the new video to the bucket
        path = upload_data(
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
