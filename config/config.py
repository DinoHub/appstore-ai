# https://rednafi.github.io/digressions/python/2020/06/03/python-configs.html
from typing import Optional

from pydantic import BaseModel, BaseSettings, Field

# class AppConfig(BaseModel):


class GlobalConfig(BaseSettings):
    ENV_STATE: Optional[str] = Field(None, env="ENV_STATE")
    MONGODB_URL : Optional[str] = None
    class Config:
        env_file: str = ".env"

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

config = FactoryConfig(GlobalConfig(MONGODB_URL="localhost:27017",ENV_STATE = 'dev').ENV_STATE)()
print(dir(config))
print(config.MONGODB_URL)