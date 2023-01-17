import torch
from pydantic import BaseSettings, Field


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

    # Model Settings
    model_name: str = Field(
        default="joeddav/xlm-roberta-large-xnli", env="MODEL_NAME"
    )
    device: str = Field(
        default="cuda:0" if torch.cuda.is_available() else "cpu"
    )


config = Config()
