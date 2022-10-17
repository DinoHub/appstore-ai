import numpy as np
import tritonclient.grpc as grpcclient
from inference_engine import SingleMediaFileIO, TextIO
from inference_engine.utils.triton import health_check
from PIL import Image

MODEL_NAME = "inception_graphdef"
TRITON_URL = "triton_inference_server:8001"

client = grpcclient.InferenceServerClient(url=TRITON_URL)


def parse_model_grpc(model_metadata, model_config):
    """
    Check the configuration of a model to make sure it meets the
    requirements for an image classification network (as expected by
    this client)
    """
    if len(model_metadata.inputs) != 1:
        raise Exception(
            "expecting 1 input, got {}".format(len(model_metadata.inputs))
        )

    if len(model_config.input) != 1:
        raise Exception(
            "expecting 1 input in model configuration, got {}".format(
                len(model_config.input)
            )
        )

    input_metadata = model_metadata.inputs[0]
    output_metadata = model_metadata.outputs

    return (input_metadata.name, output_metadata, model_config.max_batch_size)


def predict(data: SingleMediaFileIO) -> TextIO:
    # TODO: Process inputs
    image_path = data.media[0]

    input_image = Image.open(image_path).resize((229, 229))
    # Set up inputs
    inputs = [grpcclient.InferInput("input", [229, 229, 3], "FP32")]
    inputs[0].set_data_from_numpy(np.asarray(input_image))

    outputs = [
        grpcclient.InferRequestedOutput(
            "InceptionV3/Predictions/Softmax", class_count=1  # Number of class
        )
    ]

    results = client.infer(
        model_name=MODEL_NAME, inputs=inputs, outputs=outputs
    ).as_numpy("InceptionV3/Predictions/Softmax")

    # for

    return TextIO()  # TODO: Return data here
