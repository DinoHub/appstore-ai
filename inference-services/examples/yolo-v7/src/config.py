from typing import Optional, Literal

from pydantic import BaseSettings, Field



class Config(BaseSettings):
    """Define any config here.

    See here for documentation:
    https://pydantic-docs.helpmanual.io/usage/settings/
    """
    source: Literal["webcam", "upload"] = Field(default="upload", description="Source of input image", env="SOURCE")
    model_weights: str = Field(default="/app/yolov7.pt", description="Path to model weights", env="MODEL_WEIGHTS")

    nms_conf: float = Field(default=0.45, description="Non-maximum suppression confidence threshold", env="NMS_CONF")
    nms_iou: float = Field(default=0.45, description="Non-maximum suppression IoU threshold", env="NMS_IOU")

    device: str = Field(default="cpu", description="Device to use for inference", env="DEVICE")


    

config = Config()
