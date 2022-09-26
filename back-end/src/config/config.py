# https://rednafi.github.io/digressions/python/2020/06/03/python-configs.html
from typing import Optional, Union

from pydantic import BaseModel, BaseSettings, Field

# class AppConfig(BaseModel):


class GlobalConfig(BaseSettings):
    ENV_STATE: Optional[str] = Field(None, env="ENV_STATE")
    MONGODB_URL: Optional[str] = None
    MAIN_COLLECTION_NAME: Optional[str] = None
    MAX_UPLOAD_SIZE_GB: Optional[Union[int, float]] = None

    class Config:
        env_file: str = "./src/config/.env"


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

class TestingConfig(GlobalConfig):
    class Config:
        env_prefix: str = "TEST_"

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
        elif self.env_state == "test":
            return TestingConfig()


class AdminHashing(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str

    class Config:
        env_file: str = "./src/config/.env"

ENV_STATE = GlobalConfig().ENV_STATE
config = FactoryConfig(ENV_STATE)()
print(config.__repr__())
admin = AdminHashing()
