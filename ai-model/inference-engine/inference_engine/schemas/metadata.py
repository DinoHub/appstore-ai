from pydantic import BaseModel

from .io import IOSchema


class Metadata(BaseModel):
    name: str
    version: str
    description: str
    author: str
    input_schema: IOSchema
    output_schema: IOSchema
