from enum import Enum
from typing import Optional

from pydantic import AnyUrl, BaseSettings, Field


class TensorFormat(str, Enum):
    nhwc = "NHWC"  # e.g 299, 299, 3
    nchw = "NCHW"  # e.g 3, 224, 224


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
    model_name: str = Field(default="inception_graphdef", env="MODEL_NAME")
    model_version: str = Field(default="1", env="MODEL_VERSION")
    num_labels: int = Field(default=1001, env="NUM_LABELS")
    img_width: int = Field(default=299, env="IMG_WIDTH")
    img_height: int = Field(default=299, env="IMG_HEIGHT")
    img_tensor_format: TensorFormat = Field(
        default=TensorFormat.nhwc, env="TENSOR_FORMAT"
    )
    normalize_img: bool = Field(default=True, env="NORMALIZE_IMG")
    normalize_mean: float = Field(default=127.5, env="NORMALIZE_MEAN")
    normalize_std: float = Field(default=127.5, env="NORMALIZE_STD")
    input_layer: str = Field(default="input", env="INPUT_LAYER")
    output_layer: str = Field(
        default="InceptionV3/Predictions/Softmax", env="OUTPUT_LAYER"
    )


config = Config()
