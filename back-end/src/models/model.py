from enum import Enum
from typing import Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, validator

from .common import PyObjectId


class IOTypes(str, Enum):
    JSON = "JSONIO"
    Text = "TextIO"
    Media = "MediaFileIO"
    Generic = "GenericIO"


class IOSchema(BaseModel):
    io_type: IOTypes
    json_schema: Optional[Dict] = Field(None)  # JSON Schema

    """
    NOTE: when submitting an IE, a user
    may choose to add different form fields,
    with different names. Therefore,
    we need to autogenerate a schema,
    so that when presenting inference page
    to end user, we can create the 
    appropriate form. We also use this
    to show an appropriate output (e.g. showing two
    types of media files in output)
    E.g.
    
    For example, consider a Guided Diffusion model
    ```
    json_schema = {
        "prompt" : { "type" : "text" },
        "parameters": { "type" : "json", "required" : false},
        "files: { "type" : "media" }
    }
    ```
    This refers to a form with three fields:
    - Text prompt (prompt): shows up as text form field
    - Initial image (files): shows up as file upload box
    - Parameters as JSON (parameters): shows up as textarea

    Note that for certain IO types such as Media, Text,
    we use a preset schema. 
    """


class SectionModel(BaseModel):
    text: str
    title: str
    media: Optional[List[Dict]]


class InferenceEngineConfig(BaseModel):
    url: str
    input_schema: IOSchema
    output_schema: IOSchema


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
    model_details: Optional[
        SectionModel
    ]  # store model genre, format and framework
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
    inference_engine: Optional[InferenceEngineConfig]


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
    frameworks: Optional[
        List[str]
    ]  # NOTE: tbd if this should be just 1 string
    point_of_contact: Optional[str]
    owner: Optional[str]
    creator: Optional[str]
    clearml_exp_id: Optional[str]
    inference_engine: Optional[InferenceEngineConfig]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
