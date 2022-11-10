from enum import Enum
from typing import Dict, Optional

from pydantic import AnyUrl, BaseModel, Field


class InferenceEngineService(BaseModel):
    owner_id: str
    service_name: str  # use this to generate
    image_uri: str
    container_port: Optional[str]
