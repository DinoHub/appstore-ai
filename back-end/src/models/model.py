from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from bson import ObjectId
from pydantic import AnyUrl, BaseModel, Field

from ..internal.utils import to_camel_case
from .common import PyObjectId


class Artifact(BaseModel):
    artifact_type: str
    name: str
    url: AnyUrl
    timestamp: Optional[datetime]
    framework: Optional[str]


class ModelCardModelIn(BaseModel):  # Input spec
    title: str
    description: str
    performance: str
    task: str  # a task is a tag
    inference_api: AnyUrl
    tags: List[str]  # for all other tags
    frameworks: List[str]
    summary: Optional[str]
    owner: Optional[str]
    point_of_contact: Optional[str]
    clearml_exp_id: Optional[str]
    artifacts: Optional[
        List[Artifact]
    ]  # will need to use GET /experiments/{exp_id} to get this

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
    summary: Optional[str]
    description: Optional[str]
    performance: Optional[str]
    tags: Optional[List[str]]  # for all other tags
    task: Optional[str]  # a task is a tag
    frameworks: Optional[List[str]]
    point_of_contact: Optional[str]
    owner: Optional[str]
    clearml_exp_id: Optional[str]
    inference_api: Optional[AnyUrl]
    artifacts: Optional[
        Dict[str, Artifact]
    ]  # will need to use GET /experiments/{exp_id} to get this

    class Config:
        alias_generator = to_camel_case
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
