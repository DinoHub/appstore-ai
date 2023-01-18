from enum import Enum
from typing import Optional

from pydantic import AnyUrl, BaseSettings, Field


class TritonMode(str, Enum):
    polling = "POLLING"
    explicit = "EXPLICIT"


class Config(BaseSettings):
    """Define any config here.

    See here for documentation:
    https://pydantic-docs.helpmanual.io/usage/settings/
    """

    # App Settings
    # KNative assigns a $PORT environment variable to the container
    port: int = Field(
        default=8080, env="PORT", description="Gradio App Server Port"
    )
    top_k: int = Field(
        default=10, env="TOP_K", description="Top k results to show"
    )

    # Triton Settings
    triton_url: str = Field(default="localhost:8001", env="TRITON_URL")
    triton_mode: TritonMode = Field(
        default=TritonMode.polling,
        env="TRITON_MODE",
        description="If explicit, model must be loaded before sending an inference",
    )
    triton_ssl: bool = Field(
        default=False, env="TRITON_SSL", description="Flag to enable SSL"
    )
    triton_root_certs: Optional[str] = Field(
        default=None, env="TRITON_ROOT_CERTS"
    )
    triton_private_key: Optional[str] = Field(
        default=None, env="TRITON_PRIVATE_KEY"
    )
    triton_cert_chain: Optional[str] = Field(
        default=None, env="TRITON_CERT_CHAIN"
    )
    triton_client_timeout: float = Field(
        default=300, env="TRITON_CLIENT_TIMEOUT"
    )

    # Model Settings
    model_name: str = Field(default="xlm_roberta_zsl", env="MODEL_NAME")
    model_version: str = Field(default="1", env="MODEL_VERSION")


config = Config()
