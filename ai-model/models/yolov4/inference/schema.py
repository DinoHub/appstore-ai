from typing import List

from pydantic import BaseModel


class BoundingBox(BaseModel):
    class_id: int
    class_name: str
    confidence: float
    bbox: List[float] # x1, y1, x2, y2
    width: float
    height: float


class InferenceOutput(BaseModel):
    outputs: List[List[BoundingBox]]
