from typing import Optional

from pydantic import BaseModel


class InferenceEngineService(BaseModel):
    owner_id: str
    model_id: str
    image_uri: str
    container_port: Optional[int]
