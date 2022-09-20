# Inference code referenced from: https://github.com/isarsoft/yolov4-triton-tensorrt/blob/543fde846b2751d6ab394339e005e2754de22972/clients/python/client.py
import tempfile
from typing import Optional

from processing import postprocess, preprocess
from schema import InferenceOutput
import cv2
import numpy as np
import tritonclient.grpc as grpcclient
from fastapi import File, UploadFile, status
from fastapi.exceptions import HTTPException
from tritonclient.utils import InferenceServerException, triton_to_np_dtype

MODEL_NAME = "yolov4"
TRITON_URL = "localhost:8001"
HEIGHT, WIDTH = 608, 608

CHUNK_SIZE = 1024

client = grpcclient.InferenceServerClient(url=TRITON_URL)


def health_check(
    client: grpcclient.InferenceServerClient,
    model_name: str,
    model_version: str = "",
) -> bool:
    return (
        client.is_server_live()
        and client.is_server_ready()
        and client.is_model_ready(model_name=model_name, model_version=model_version)
    )


async def predict(media: UploadFile = File()):
    # Check health of model
    try:
        if not health_check(client, MODEL_NAME):
            raise InferenceServerException
    except InferenceServerException:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to access either Triton Inference Server or Model",
        )
    # Download file (currently assume that file size has been validated)
    try:
        with tempfile.NamedTemporaryFile(delete=False) as f:
            while content := media.file.read(CHUNK_SIZE):
                f.write(content)
            # Assume that its an image (for now anyways)
        input_image = cv2.imread(f.name)
        if input_image is None:
            raise IOError
    except IOError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error when attempting to read file input",
        )

    # Perform processing on image
    input_image_buffer = preprocess(input_image, [WIDTH, HEIGHT])
    input_image_buffer = np.expand_dims(input_image_buffer, axis=0)  # add batch dim

    # Set up input
    inputs = [grpcclient.InferInput("input", [1, 3, HEIGHT, WIDTH], "FP32")]
    outputs = [grpcclient.InferRequestedOutput("detections")]

    inputs[0].set_data_from_numpy(input_image_buffer)

    # Inference
    results = client.infer(
        model_name=MODEL_NAME, inputs=inputs, outputs=outputs
    ).as_numpy("detections")

    # process detections (run non-max supression to improve quality of results)
    output = postprocess(
        results,
        input_image.shape[1],
        input_image.shape[0],
        [WIDTH, HEIGHT],
    )
    return InferenceOutput(
        outputs=output
    )
    # return {"inputs": [input_image], "outputs": output}
