from typing import Optional

from pydantic import BaseSettings, Field


class Config(BaseSettings):
    """Define any config here.

    See here for documentation:
    https://pydantic-docs.helpmanual.io/usage/settings/
    """

    # KNative assigns a $PORT environment variable to the container
    port: int = Field(
        default=8080, env="PORT", description="Gradio App Server Port"
    )

    message: str = Field(default="Hello world", env="MSG")


config = Config()
