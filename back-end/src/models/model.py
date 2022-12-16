from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from ..internal.utils import to_camel_case
from .experiment import LinkedExperiment
from .dataset import LinkedDataset
from .common import PyObjectId


class Artifact(BaseModel):
    artifact_type: str = Field(..., alias="artifactType")
    name: str
    url: str
    timestamp: Optional[datetime]
    framework: Optional[str]

    class Config:
        allow_population_by_field_name = True


class ModelCardModelIn(BaseModel):  # Input spec
    title: str
    markdown: str
    performance: str
    task: str  # a task is a tag
    inference_service_name: Optional[str]
    video_path: Optional[str]
    tags: List[str]  # for all other tags
    frameworks: List[str]
    description: Optional[str]
    explanation: Optional[str]
    usage: Optional[str]
    limitations: Optional[str]
    owner: Optional[str]  # NOTE: This is different from creator_user_id
    point_of_contact: Optional[str]
    artifacts: Optional[
        List[Artifact]
    ]  # will need to use GET /experiments/{exp_id} to get this
    experiment: Optional[LinkedExperiment]
    dataset: Optional[LinkedDataset]

    class Config:
        alias_generator = to_camel_case


class ModelCardModelDB(ModelCardModelIn):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creator_user_id: str  # to be dynamically put in by FastAPI
    model_id: str  # to be generated on back-end
    created: datetime
    last_modified: datetime

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdateModelCardModel(BaseModel):
    title: Optional[str]
    description: Optional[str]
    explanation: Optional[str]
    usage: Optional[str]
    limitations: Optional[str]
    markdown: Optional[str]
    performance: Optional[str]
    tags: Optional[List[str]]  # for all other tags
    task: Optional[str]  # a task is a tag
    frameworks: Optional[List[str]]
    point_of_contact: Optional[str]
    owner: Optional[str]
    inference_service_name: Optional[str]
    artifacts: Optional[
        List[Artifact]
    ]  # will need to use GET /experiments/{exp_id} to get this
    experiment: Optional[LinkedExperiment]
    dataset: Optional[LinkedDataset]

    class Config:
        alias_generator = to_camel_case
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
