"""Data models for bucket endpoints."""
from pydantic import BaseModel, validator


class VideoUploadResponse(BaseModel):
    """Response model for video upload."""

    video_location: str

    @validator("video_location")
    def validate_video_location(cls, value):
        """Validate video location."""
        if not value.startswith("s3://"):
            raise ValueError("Video location must point to an S3 bucket.")
        return value
