"""Data models for bucket endpoints."""
from pydantic import BaseModel


class VideoUploadResponse(BaseModel):
    """Response model for video upload."""

    video_location: str
