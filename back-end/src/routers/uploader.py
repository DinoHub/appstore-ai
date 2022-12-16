from fastapi import APIRouter, Request, status, UploadFile
from fastapi.responses import JSONResponse


router = APIRouter(prefix="/upload", tags=["Uploads"])


@router.post("/video")
async def upload_video(video: UploadFile):
    print(video.content_type)
    if "video" in video.content_type:
        print(video.filename)
        print(video.content_type)
        print(dir(video))
        print(dir(video.file))
        print(video.file)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=f"Validation of video cleared",
        )
    else:
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=f"Validation of video not cleared",
        )
