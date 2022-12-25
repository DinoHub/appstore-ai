from fastapi import APIRouter, Request, status, UploadFile, Depends, HTTPException
from fastapi.responses import JSONResponse
import io
from datetime import timedelta
from colorama import Fore

from ..internal.minio_client import minio_api_client
from ..config.config import config
from ..models.iam import TokenData
from ..internal.auth import get_current_user

router = APIRouter(prefix="/buckets", tags=["buckets"])
s3_client = minio_api_client()
bucket_name = config.MINIO_BUCKET_NAME


@router.post("/video", status_code=status.HTTP_200_OK)
def upload_video(video: UploadFile, user: TokenData = Depends(get_current_user)):
    try:
        if not user.user_id:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if "video" in video.content_type:
            value_as_a_stream = io.BytesIO(video.file.read())
            video_length = len(value_as_a_stream.read())
            value_as_a_stream.seek(0)
            s3_client.put_object(
                bucket_name=bucket_name,
                object_name=f"videos/{video.filename}",
                data=value_as_a_stream,
                length=video_length,
                content_type=video.content_type,
            )
            # NOTE: this should be done when attemping retrieval as it is required
            # item_location = s3_client.get_presigned_url(
            #     "GET",
            #     bucket_name,
            #     f"videos/{video.filename}",
            #     expires=timedelta(days=7),
            # )
            return_pkg = {"video_location": f"videos/{video.filename}"}
            return return_pkg
        else:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=f"Validation of video not cleared",
            )
    except Exception as e:
        print(f"{Fore.RED}ERROR{Fore.WHITE}:\t  {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f"Something went wrong the upload",
        )



@router.post("/image", status_code=status.HTTP_200_OK)
def upload_image(image: UploadFile, return_base64: bool = False):
    try:
        if "image" in image.content_type:
            value_as_a_stream = io.BytesIO(image.file.read())
            image_length = len(value_as_a_stream.read())
            value_as_a_stream.seek(0)
            s3_client.put_object(
                bucket_name=bucket_name,
                object_name=f"images/{image.filename}",
                data=value_as_a_stream,
                length=image_length,
                content_type=image.content_type,
            )
            # item_location = s3_client.get_presigned_url(
            #     "GET",
            #     bucket_name,
            #     f"images/{image.filename}",
            #     expires=timedelta(days=30),
            # )
            return_pkg = {}
            # print(item_location)
        else:
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=f"Validation of image not cleared",
            )
    except Exception as e:
        print(f"{Fore.RED}ERROR{Fore.WHITE}:\t  {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f"Something went wrong the upload",
        )
