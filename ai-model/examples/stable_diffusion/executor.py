from typing import Any, List, Tuple

import numpy as np
import tritonclient.grpc as grpcclient
from inference_engine import MediaFileIO, TextIO
from inference_engine.utils.triton import health_check
from PIL import Image
from tritonclient.utils import InferenceServerException

MODEL_NAME = "stable_diffusion"
MODEL_VERSION = "1"
TRITON_URL = "172.20.0.3:8001"

BATCH_SIZE = 1
SAMPLES = 1
STEPS = 45
GUIDANCE_SCALE = 7.5
SEED = 42
MAX_IMAGES_PER_ROW = 3

client = grpcclient.InferenceServerClient(url=TRITON_URL)


def image_grid(imgs: List[Image.Image], rows: int, cols: int) -> Image.Image:
    w, h = imgs[0].size
    grid = Image.new("RGB", size=(cols * w, rows * h))
    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid


def predict(text: TextIO) -> MediaFileIO:

    # Check health of model
    text = text.text
    if not health_check(client, MODEL_NAME, MODEL_VERSION):
        raise InferenceServerException

    inputs = [
        grpcclient.InferInput("PROMPT", shape=(BATCH_SIZE,), datatype="BYTES"),
        grpcclient.InferInput(
            "SAMPLES", shape=(BATCH_SIZE,), datatype="INT32"
        ),
        grpcclient.InferInput("STEPS", shape=(BATCH_SIZE,), datatype="INT32"),
        grpcclient.InferInput(
            "GUIDANCE_SCALE", shape=(BATCH_SIZE,), datatype="FP32"
        ),
        grpcclient.InferInput("SEED", shape=(BATCH_SIZE,), datatype="INT64"),
    ]

    outputs = [grpcclient.InferRequestedOutput("IMAGES")]

    # Fill in inputs
    value_types: List[Tuple[Any, type]] = [
        (text, object),
        (SAMPLES, np.int32),
        (STEPS, np.int32),
        (GUIDANCE_SCALE, np.float32),
        (SEED, np.int64),
    ]
    for idx, (value, dtype) in enumerate(value_types):
        inputs[idx].set_data_from_numpy(
            np.asarray([value] * BATCH_SIZE, dtype=dtype)
        )

    # Make Inference
    images = client.infer(
        model_name=MODEL_NAME,
        model_version=MODEL_VERSION,
        inputs=inputs,
        outputs=outputs,
    ).as_numpy("IMAGES")

    # Rescale Image
    if images.ndim == 3:
        images = images[None, ...]

    images = (images * 255).round().astype("uint8")
    images = [Image.fromarray(image) for image in images]

    images = image_grid(images, rows=1, cols=1)
    images.save("image.jpg", format="JPEG")

    return MediaFileIO(media=["image.jpg"])
