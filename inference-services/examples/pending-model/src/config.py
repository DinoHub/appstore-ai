from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List

class BaseConfig(BaseSettings):
    """Define any config here.

    See here for documentation:
    https://pydantic-docs.helpmanual.io/usage/settings/
    """
    # KNative assigns a $PORT environment variable to the container
    port: int = Field(
        default=8080, env="PORT", description="Gradio App Server Port"
    )


config = BaseConfig()