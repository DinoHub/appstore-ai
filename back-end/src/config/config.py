"""This module contains the configuration for the application.
Depending on the environment, the configuration will be different.
"""


# https://rednafi.github.io/digressions/python/2020/06/03/python-configs.html
import os
from enum import Enum
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, BaseSettings, Field, MongoDsn, validator

from ..models.engine import ServiceBackend


class Environment(str, Enum):
    """Enum for the different environments."""

    DEV = "dev"
    STG = "stg"
    PROD = "prod"
    TEST = "test"


class GlobalConfig(BaseSettings):
    """Global configuration for the application."""

    ENV_STATE: Environment = Field(default=Environment.DEV, env="ENV_STATE")

    # General Settings
    # CORS ORIGINS
    # e.g: '["http://localhost", "http://localhost:4200", "http://localhost:3000", \
    # "http://localhost:8080", "http://local.dockertoolbox.tiangolo.com"]'
    FRONTEND_HOST: List[AnyHttpUrl] = []
    MAX_UPLOAD_SIZE_GB: Union[int, float] = Field(default=10)
    SECURE_COOKIES: bool = Field(default=False)  # set to True if site is HTTPS

    # Authentication Settings
    ALGORITHM: str = Field(default="HS256")
    SECRET_KEY: Optional[
        str
    ] = None  # NOTE: set to none as a hack to get Sphinx to build correctly
    FIRST_SUPERUSER_ID: Optional[str] = None
    FIRST_SUPERUSER_PASSWORD: Optional[str] = None

    # Database Settings
    DB_NAME: str = Field(default="appStoreDB")
    MONGO_DSN: Optional[MongoDsn] = None
    MONGO_USERNAME: Optional[str] = None
    MONGO_PASSWORD: Optional[str] = None

    # Object Storage Settings
    MINIO_DSN: Optional[str] = None
    MINIO_API_HOST: Optional[str] = None
    MINIO_BUCKET_NAME: str = Field(default="model-zoo")
    MINIO_TLS: bool = Field(default=False)
    MINIO_API_ACCESS_KEY: Optional[str] = None
    MINIO_API_SECRET_KEY: Optional[str] = None

    # Kubernetes and Inference Service Settings
    IE_NAMESPACE: Optional[str] = None
    IE_SERVICE_TYPE: ServiceBackend = Field(default=ServiceBackend.EMISSARY)
    IE_DEFAULT_PROTOCOL: str = Field(default="http")
    IE_DOMAIN: Optional[str] = None
    IE_INGRESS_NAME: Optional[str] = None  # TODO: Integrate this
    IE_INGRESS_NAMESPACE: Optional[str] = None  # TODO: Integrate this
    K8S_HOST: Optional[str] = None
    K8S_API_KEY: Optional[str] = None

    # ClearML Settings
    CLEARML_CONFIG_FILE: Optional[str] = None
    CLEARML_WEB_HOST: Optional[str] = None
    CLEARML_API_HOST: Optional[str] = None
    CLEARML_FILES_HOST: Optional[str] = None
    CLEARML_API_ACCESS_KEY: Optional[str] = None
    CLEARML_API_SECRET_KEY: Optional[str] = None

    @validator("FRONTEND_HOST", pre=True)
    def assemble_cors_origins(
        cls, v: Union[str, List[str]]
    ) -> Union[List[str], str]:
        """Convert a string array of the frontend origins
        to an actual array

        Args:
            v (Union[str, List[str]]): _description_

        Raises:
            ValueError: _description_

        Returns:
            Union[List[str], str]: _description_
        """
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        """Pydantic config class."""

        env_file: str = "./src/config/.env"

    def set_envvar(self):
        """Temporarily set environment variables.
        This change will not be permanent, so no
        need to worry about overriding system
        envvars.
        """
        for key, value in self.dict(exclude_none=True).items():
            # Save config to environment
            os.environ[key] = str(value)


class DevConfig(GlobalConfig):
    """Development configuration.
    Inherits from GlobalConfig, using
    environment variables that start with
    `DEV_` as the default values.
    """

    class Config:
        """Pydantic config class.
        Set the environment variable prefix
        to `DEV_`.
        """

        env_prefix: str = "DEV_"


class StagingConfig(GlobalConfig):
    """Staging configuration.
    Inherits from GlobalConfig, using
    environment variables that start with
    `STG_` as the default values.
    """

    class Config:
        """Pydantic config class.
        Set the environment variable prefix
        to `STG_`.
        """

        env_prefix: str = "STG_"


class ProductionConfig(GlobalConfig):
    """Production configuration.
    Inherits from GlobalConfig, using
    environment variables that start with
    `PROD_` as the default values.
    """

    class Config:
        """Pydantic config class."""

        env_prefix: str = "PROD_"


class TestingConfig(GlobalConfig):
    """Testing configuration used for unit tests.
    Inherits from GlobalConfig, using
    environment variables that start with
    `TEST_` as the default values.
    """

    class Config:
        """Pydantic config class."""

        env_prefix: str = "TEST_"


class FactoryConfig:
    """Return config instance based on `ENV_STATE` variable"""

    def __init__(self, env_state: Optional[str]):
        self.env_state = env_state

    def __call__(self):
        if self.env_state == Environment.DEV:
            return DevConfig()
        elif self.env_state == Environment.STG:
            return StagingConfig()
        elif self.env_state == Environment.PROD:
            return ProductionConfig()
        elif self.env_state == Environment.TEST:
            return TestingConfig()
        else:
            raise ValueError(f"Unsupported config: {self.env_state}")


ENV_STATE = GlobalConfig().ENV_STATE  # Based on environment variables
config: GlobalConfig = FactoryConfig(
    ENV_STATE
)()  # Initialize config based on ENV_STATE

if config is not None:
    # Set environment variables based on config
    # this is useful for clearml credentials
    # where the api key needs to be set as an
    # environment variable
    config.set_envvar()
