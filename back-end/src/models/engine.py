from datetime import datetime
from typing import Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from ..internal.utils import to_camel_case
from .common import PyObjectId


class CreateInferenceEngineService(BaseModel):
    model_id: str  # NOTE: actually model title, will convert to model id in backend
    image_uri: str
    container_port: Optional[int]
    external_dns: Optional[str]
    env: Optional[dict]

    class Config:
        alias_generator = to_camel_case


class InferenceEngineService(CreateInferenceEngineService):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    inference_url: str
    owner_id: str
    service_name: str
    created: datetime
    last_modified: datetime

    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdateInferenceEngineService(BaseModel):
    image_uri: str
    container_port: Optional[int]
    env: Optional[dict]

    class Config:
        alias_generator = to_camel_case
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
