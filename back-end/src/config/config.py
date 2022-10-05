# https://rednafi.github.io/digressions/python/2020/06/03/python-configs.html
import os
from typing import Optional, Union

from pydantic import BaseModel, BaseSettings, Field

# class AppConfig(BaseModel):


class GlobalConfig(BaseSettings):
    ENV_STATE: Optional[str] = Field(None, env="ENV_STATE")
    MONGODB_URL: Optional[str] = None
    MAIN_COLLECTION_NAME: Optional[str] = None
    MAX_UPLOAD_SIZE_GB: Optional[Union[int, float]] = None
    CLEARML_CONFIG_FILE: Optional[str] = None
    K8S_HOST: Optional[str] = None
    K8S_API_KEY: Optional[str] = None
    # CLEARML_API_HOST: Optional[str] = None
    # CLEARML_WEB_HOST: Optional[str] = None
    # CLEARML_FILES_HOST: Optional[str] = None
    # CLEARML_NO_DEFAULT_SERVER: Optional[int] = None

    class Config:
        env_file: str = "./src/config/.env"

    def set_envvar(self):
        """Temporarily set environment variables.
        This change will not be permanent, so no
        need to worry about overriding system
        envvars.
        """
        for key, value in self.dict(exclude_none=True).items():
            # Save config to environment
            print(f"Setting {key} to {value}")
            os.environ[key] = str(value)


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
        elif self.env_state is None:
            return None
        else:
            raise ValueError(f"Unsupported config: {self.env_state}")


class ClearMLConfig(BaseSettings):
    CLEARML_WEB_HOST: str = None
    CLEARML_API_HOST: str = None
    CLEARML_FILES_HOST: str = None
    CLEARML_API_ACCESS_KEY: str = None
    CLEARML_API_SECRET_KEY: str = None

    class Config:
        env_file: str = "./src/config/.env"


class AdminHashing(BaseSettings):
    SECRET_KEY: str
    ALGORITHM: str = "HS256"

    class Config:
        env_file: str = "./src/config/.env"


ENV_STATE = GlobalConfig().ENV_STATE
config = FactoryConfig(ENV_STATE)()
if config is not None:
    config.set_envvar()
print(config.__repr__())
admin = AdminHashing()
clear_conf = ClearMLConfig()
