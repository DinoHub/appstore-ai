from enum import Enum
from typing import Dict, Optional

from pydantic import AnyUrl, BaseModel, Field


class InferenceEngineService(BaseModel):
    owner_id: str
    model_id: str
    image_uri: str
    container_port: Optional[int]
