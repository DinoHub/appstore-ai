# https://rednafi.github.io/digressions/python/2020/06/03/python-configs.html
from typing import Optional, Union

from pydantic import BaseModel, BaseSettings, Field

# class AppConfig(BaseModel):


class GlobalConfig(BaseSettings):
    ENV_STATE: Optional[str] = Field(None, env="ENV_STATE")
    MONGODB_URL: Optional[str] = None
    MAX_UPLOAD_SIZE_GB: Optional[Union[int, float]] = None

    class Config:
        env_file: str = "./config/.env"

class DevConfig(GlobalConfig):
    class Config:
        env_prefix: str = "DEV_"
        # TODO: add secrets_dir to support loading secrets


class StagingConfig(GlobalConfig):
    class Config:
        env_prefix: str = "STG_"
        # TODO: add secrets_dir to support loading secrets


class ProductionConfig(GlobalConfig):
    class Config:
        env_prefix: str = "PROD_"
        # TODO: add secrets_dir to support loading secrets


class FactoryConfig:
    """Return config instance based on `ENV_STATE` variable"""

    def __init__(self, env_state: Optional[str]):
        self.env_state = env_state

    def __call__(self):
        if self.env_state == "dev":
            return DevConfig()
        elif self.env_state == "stg":
            return StagingConfig()
        elif self.env_state == "prod":
            return ProductionConfig()


config = FactoryConfig(GlobalConfig().ENV_STATE)()
print(config.__repr__())
