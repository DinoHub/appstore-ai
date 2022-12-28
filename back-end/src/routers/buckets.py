import io

from colorama import Fore
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from minio import Minio

from ..config.config import config
from ..internal.auth import get_current_user
from ..internal.minio_client import minio_api_client, upload_data
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
                f"videos/{video.filename}",
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
