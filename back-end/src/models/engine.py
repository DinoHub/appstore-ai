"""Data models for inference engine services."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from bson import ObjectId
from pydantic import BaseModel, Field, PositiveInt, constr, validator

from ..internal.utils import sanitize_for_url, to_camel_case
from .common import PyObjectId

# NOTE: disabled ability to set resource limits
# TODO: Improve implementation of resource limits
# class ResourceLimits(BaseModel):
#     cpu_cores: float = Field(
#         default=1, gt=0, lt=16, description="CPU cores (0.5, 1, 2, 4, 8, 16)"
#     )
#     memory_gb: int = Field(
#         default=2,
#         gt=0,
#         lt=32,
#         description="Memory in GB (1, 2, 4, 8, 16, 32)",
#     )

IMAGE_URI_REGEX = "^(?:(?=[^:\/]{1,253})(?!-)[a-zA-Z0-9-]{1,63}(?<!-)(?:\.(?!-)[a-zA-Z0-9-]{1,63}(?<!-))*(?::[0-9]{1,5})?/)?((?![._-])(?:[a-z0-9._-]*)(?<![._-])(?:/(?![._-])[a-z0-9._-]*(?<![._-]))*)(?::(?![.-])[a-zA-Z0-9_.-]{1,128})?$"

ContainerURI = constr(regex=IMAGE_URI_REGEX)


class ServiceBackend(str, Enum):
    """Enum for service backend."""

    KNATIVE = "knative"  # knative-serving
    EMISSARY = "emissary"  # emissary-ingress


class K8SPhase(str, Enum):
    """Enum for K8S phase."""

    PENDING = "Pending"
    RUNNING = "Running"
    SUCCEEDED = "Succeeded"
    FAILED = "Failed"
    UNKNOWN = "Unknown"


class InferenceServiceStatus(BaseModel):
    service_name: str
    status: K8SPhase = K8SPhase.UNKNOWN
    message: str = ""
    ready: bool = True
    schedulable: bool = True
    expected_replicas: int = Field(default=1, ge=0)

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys.
        """

        allow_population_by_field_name = True
        alias_generator = to_camel_case


class CreateInferenceEngineService(BaseModel):
    """Request model for creating an inference engine service."""

    model_id: str  # NOTE: actually model title, will convert to model id in backend
    image_uri: ContainerURI
    # resource_limits: ResourceLimits
    container_port: Optional[PositiveInt] = None
    env: Optional[Dict[str, str]] = None
    # float to allow for fractional GPUs
    num_gpus: float = Field(default=0, ge=0, le=2)

    @validator("model_id")
    def sanitize_model_name(cls, v: str) -> str:
        """Generates a URL safe model id if one is not provided.

        Args:
            v (str): The model name.

        Returns:
            str: Generated model id.
        """
        return sanitize_for_url(v)

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys.
        """

        alias_generator = to_camel_case


class InferenceEngineService(CreateInferenceEngineService):
    """Data model for inference engine service in database."""

    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    inference_url: str
    owner_id: str
    service_name: str
    created: datetime
    last_modified: datetime
    host: str
    path: str
    protocol: str = Field(default="http")
    backend: ServiceBackend

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys and to convert
        ObjectId to str when returning JSON.
        """

        alias_generator = to_camel_case
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class UpdateInferenceEngineService(BaseModel):
    """Request model for updating an inference engine service."""

    image_uri: ContainerURI
    container_port: Optional[PositiveInt] = None
    # resource_limits: ResourceLimits
    env: Optional[dict] = None
    num_gpus: float = Field(default=0, ge=0, le=2)

    class Config:
        """Pydantic config to allow creation of data model
        from a JSON object with camelCase keys.
        """

        alias_generator = to_camel_case
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
