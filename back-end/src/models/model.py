from typing import Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from .common import PyObjectId


class SectionModel(BaseModel):
    text: str
    title: str
    media: Optional[List[Dict]]


class ModelCardModelIn(BaseModel):  # Input spec
    title: str
    # NOTE: flattened sections to make schema easier
    # description: Dict[SectionTypes, Section]
    description: SectionModel
    limitations: SectionModel
    metrics: SectionModel
    explanation: SectionModel
    deployment: SectionModel
    performance: Optional[SectionModel]
    model_details: Optional[SectionModel]  # store model genre, format and framework
    datetime: str
    tags: List[str]  # for all other tags
    task: str  # a task is a tag
    frameworks: List[
        str
    ]  # TODO: decide if this should be a singular tag or allow multiple
    point_of_contact: str
    owner: str
    creator: Optional[str]
    # TODO: Figure out model source stuff
    clearml_exp_id: Optional[str]
    inference_url: str
    output_generator_url: Optional[str]


class ModelCardModelDB(ModelCardModelIn):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class FindModelCardModel(BaseModel):
    title: Optional[str]
    tags: Optional[List[str]]
    task: Optional[str]
    frameworks: Optional[List[str]]
    point_of_contact: Optional[str]
    owner: Optional[str]
    creator: Optional[str]
    sort: Optional[List[List[str]]]  # [(sort col, sort direction)]
    return_attrs: Optional[List[str]]


class UpdateModelCardModel(BaseModel):
    title: Optional[str]
    description: Optional[SectionModel]
    limitations: Optional[SectionModel]
    metrics: Optional[SectionModel]
    explanation: Optional[SectionModel]
    deployment: Optional[SectionModel]
    performance: Optional[SectionModel]
    model_details: Optional[SectionModel]
    datetime: Optional[str]
    tags: Optional[List[str]]
    task: Optional[str]
    frameworks: Optional[List[str]]  # NOTE: tbd if this should be just 1 string
    point_of_contact: Optional[str]
    owner: Optional[str]
    creator: Optional[str]
    clearml_exp_id: Optional[str]
    inference_url: Optional[str]
    output_generator_url: Optional[str]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
