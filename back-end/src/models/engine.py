from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field


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


class InferenceEngine(BaseModel):
    owner_id: str
    # input_schema: IOSchema # NOTE: Deprecated
    # output_schema: IOSchema
    service_url: str


class InferenceEngineService(BaseModel):
    owner_id: str
    service_name: str  # use this to generate
    image_uri: str
