from typing import Dict, List, Optional

from bson import ObjectId
from pydantic import BaseModel, Field

from .common import PyObjectId, SecurityClassification


class Section(BaseModel):
    text: str
    title: str
    media: Optional[List[Dict]]


class PerformanceSection(Section):
    media: Optional[List[Dict[str, Dict[str, Dict[str, List[float]]]]]]


class ModelCard(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    # NOTE: flattened sections to make schema easier
    # description: Dict[SectionTypes, Section]
    description: Section
    limitations: Section
    metrics: Section
    explanation: Section
    deployment: Section
    performance: Optional[PerformanceSection]
    model_details: Optional[Section]  # store model genre, format and framework
    datetime: str
    tags: List[str]
    security_classification: SecurityClassification
    owner: str
    creator: Optional[str]
    # TODO: Figure out model source stuff
    clearml_exp_id: Optional[str]
    inference_url: str
    output_generator_url: str

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
