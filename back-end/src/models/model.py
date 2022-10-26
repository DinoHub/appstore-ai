from datetime import datetime
from typing import Dict, List, Optional

from bson import ObjectId
from pydantic import AnyUrl, BaseModel, Field

from .common import PyObjectId


class ModelCardModelIn(BaseModel):  # Input spec
    model_id: str  # unique id
    title: str
    description: str
    performance: str
    created: datetime
    last_modified: datetime
    tags: List[str]  # for all other tags
    task: str  # a task is a tag
    frameworks: List[str]
    point_of_contact: Optional[str]
    owner: Optional[str]
    clearml_exp_id: Optional[str]
    inference_api: AnyUrl


class ModelCardModelDB(ModelCardModelIn):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    creator_user_id: str  # to be dynamically put in by FastAPI

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FindModelCardModel(BaseModel):
    model_id: Optional[str]
    creator_user_id: Optional[str]
    title: Optional[str]
    tags: Optional[List[str]]
    task: Optional[str]
    frameworks: Optional[List[str]]
    point_of_contact: Optional[str]
    owner: Optional[str]
    sort: Optional[List[List[str]]]  # [(sort col, sort direction)]
    return_attrs: Optional[List[str]]


class UpdateModelCardModel(BaseModel):
    model_id: Optional[str]  # unique id
    title: Optional[str]
    description: Optional[str]
    performance: Optional[str]
    tags: Optional[List[str]]  # for all other tags
    task: Optional[str]  # a task is a tag
    frameworks: Optional[List[str]]
    point_of_contact: Optional[str]
    owner: Optional[str]
    clearml_exp_id: Optional[str]
    inference_api: Optional[AnyUrl]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
