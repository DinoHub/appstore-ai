from pydantic import AnyUrl, BaseSettings, Field


class Config(BaseSettings):
    """Define any config here.

    See here for documentation:
    https://pydantic-docs.helpmanual.io/usage/settings/
    """
    # KNative assigns a $PORT environment variable to the container
    port: int = Field(default=8080, env="PORT",description="Gradio App Server Port")

    {%- if cookiecutter.inference_backend == "Triton" -%}
    triton_url: AnyUrl = Field(default="localhost:8001", env="TRITON_URL") 
    triton_mode: str = Field(default="POLLING", env="TRITON_MODE")
    {% endif %}

config = Config()
