"""Data models for model cards."""
from typing import List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, validator

from ..internal.utils import sanitize_for_url, to_camel_case
from .common import Artifact, PyObjectId
from .dataset import LinkedDataset
from .experiment import LinkedExperiment


class ModelCardModelIn(BaseModel):  # Input spec
    """Request model for creating a model card."""

    title: str = Field(max_length=50)
    markdown: str
    performance: str
    task: str  # a task is a tag
    inference_service_name: Optional[str] = None
    video_location: Optional[str] = None
    tags: List[str]  # for all other tags
    frameworks: List[str]
    description: Optional[str] = None
    explanation: Optional[str] = None
    usage: Optional[str] = None
    limitations: Optional[str] = None
    owner: Optional[str] = None  # NOTE: This is different from creator_user_id
    point_of_contact: Optional[str] = None
    artifacts: Optional[
        List[Artifact]
    ] = None  # will need to use GET /experiments/{exp_id} to get this
    experiment: Optional[LinkedExperiment] = None
    dataset: Optional[LinkedDataset] = None

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys.
        """

        alias_generator = to_camel_case


class ModelCardModelDB(ModelCardModelIn):
    """Data model for model card in database.
    Contain additional fields for database that will
    be filled in as part of the controller logic.
    """

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creator_user_id: str  # to be dynamically put in by FastAPI
    model_id: str  # to be generated on back-end
    created: str
    last_modified: str

    @validator("model_id")
    def sanitize_model_name(cls, v: str) -> str:
        """Generates a URL safe model id if one is not provided.

        Args:
            v (str): The model name.

        Returns:
            str: Generated model id.
        """
        return sanitize_for_url(v)

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys and to convert
        ObjectId to str when returning JSON.
        """

        alias_generator = to_camel_case
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdateModelCardModel(BaseModel):
    """Request model for updating a model card.
    All fields are optional, to allow for partial updates.
    """

    title: Optional[str] = Field(default=None, max_length=50)
    description: Optional[str] = None
    explanation: Optional[str] = None
    usage: Optional[str] = None
    limitations: Optional[str] = None
    markdown: Optional[str] = None
    performance: Optional[str] = None
    tags: Optional[List[str]] = None  # for all other tags
    task: Optional[str] = None  # a task is a tag
    frameworks: Optional[List[str]] = None
    point_of_contact: Optional[str] = None
    owner: Optional[str] = None
    video_location: Optional[str] = None
    inference_service_name: Optional[str] = None
    artifacts: Optional[
        List[Artifact]
    ] = None  # will need to use GET /experiments/{exp_id} to get this
    experiment: Optional[LinkedExperiment] = None
    dataset: Optional[LinkedDataset] = None

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys.
        """

        alias_generator = to_camel_case
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class GetFilterResponseModel(BaseModel):
    """Response model for getting filter options for model cards."""

    tags: List[str]
    frameworks: List[str]
    tasks: List[str]


class SearchModelResponse(BaseModel):
    """Response model for searching model cards."""

    results: List
    total: int = Field(..., ge=0)


class ModelCardCompositeKey(BaseModel):
    """General model for the composite key for models of id and creator id"""

    model_id: str
    creator_user_id: str


class ModelCardPackage(BaseModel):
    """Model for compiling list of composite keys of the models"""

    card_package: List[ModelCardCompositeKey]
