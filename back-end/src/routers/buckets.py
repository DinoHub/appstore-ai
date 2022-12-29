import io
import uuid

from colorama import Fore
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status, Form, File
from fastapi.responses import JSONResponse
from minio import Minio

from ..config.config import config
from ..internal.auth import get_current_user
from ..internal.minio_client import minio_api_client, upload_data, remove_data
from ..models.iam import TokenData

router = APIRouter(prefix="/buckets", tags=["buckets"])

BUCKET_NAME = config.MINIO_BUCKET_NAME or "default"


@router.post("/video", status_code=status.HTTP_200_OK)
def upload_video(
    video: UploadFile,
    user: TokenData = Depends(get_current_user),
    s3_client: Minio = Depends(minio_api_client),
):
    try:
        if not user.user_id:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        if "video" in video.content_type:
            path = upload_data(
                s3_client,
                video.file.read(),
                f"videos/{uuid.uuid4().hex}.{video.content_type.replace('video/','')}",
                BUCKET_NAME,
                video.content_type,
            )
            # NOTE: this should be done when attemping retrieval as it is required
            # item_location = s3_client.get_presigned_url(
            #     "GET",
            #     bucket_name,
            #     f"videos/{video.filename}",
            #     expires=timedelta(days=7),
            # )
            return {"video_location": path}
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


@router.put("/video", status_code=status.HTTP_200_OK)
def replace_video(
    new_video: UploadFile = Form(),
    old_video_location: str = Form(),
    user: TokenData = Depends(get_current_user),
    s3_client: Minio = Depends(minio_api_client),
):
    try:
        if not user.user_id:
            return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if "video" in new_video.content_type:

            # remove the old video inside the bucket
            video_location = old_video_location.replace(
                f"{config.MINIO_API_HOST}/{config.MINIO_BUCKET_NAME}/", ""
            )
            remove_data(s3_client, video_location, config.MINIO_BUCKET_NAME)

            # upload the new video to the bucket
            path = upload_data(
                s3_client,
                new_video.file.read(),
                f"videos/{uuid.uuid4().hex}.{new_video.content_type.replace('video/','')}",
                BUCKET_NAME,
                new_video.content_type,
            )
            return {"video_location": path}

        # return this if new file is not video
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f"Something went wrong the removal of the video",
        )
    except Exception as e:
        print(f"{Fore.RED}ERROR{Fore.WHITE}:\t  {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=f"Something went wrong the removal of the video",
        )


# @router.post("/image", status_code=status.HTTP_200_OK)
# def upload_image(image: UploadFile, s3_client: Minio = Depends(minio_api_client)):
#     try:
#         if "image" in image.content_type:
#             path = upload_data(
#                 s3_client,
#                 image.file.read(),
#                 f"images/{image.filename}",
#                 BUCKET_NAME,
#                 image.content_type,
#             )
#             # item_location = s3_client.get_presigned_url(
#             #     "GET",
#             #     bucket_name,
#             #     f"images/{image.filename}",
#             #     expires=timedelta(days=30),
#             # )
#             # print(item_location)
#             return {"image_location": path}
#         else:
#             return JSONResponse(
#                 status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#                 content=f"Validation of image not cleared",
#             )
#     except Exception as e:
#         print(f"{Fore.RED}ERROR{Fore.WHITE}:\t  {e}")
#         return JSONResponse(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             content=f"Something went wrong the upload",
#         )
