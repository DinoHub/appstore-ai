from typing import List

from numpy.typing import NDArray
from pydantic import BaseModel


class BoundingBox(BaseModel):
    class_id: int
    confidence: float
    bbox: List[float]
    width: float
    height: float


class InferenceOutput(BaseModel):
    outputs: List[BoundingBox]
