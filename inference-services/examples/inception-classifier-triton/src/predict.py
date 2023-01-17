import logging
from typing import Any, Dict, List, Optional, Union

import gradio.inputs as gr_inputs
import gradio.outputs as gr_outputs
import numpy as np
import tritonclient.grpc as tr
from config import TensorFormat, config
from triton_utils import get_client, load_model, unload_model

inputs = gr_inputs.Image(shape=(config.img_width, config.img_height))
outputs = gr_outputs.Label(num_top_classes=config.top_k)
examples: Optional[Union[List[Any], List[List[Any]], str]] = None


def predict(image: np.ndarray) -> Dict[str, float]:
    """Takes in an image, and
    calls Triton to infer it's class

    :param image: Image
    :type image: np.ndarray
    :return: Predicted classes with confidence
    :rtype: Dict[str, float]
    """
    # Initialize Triton GRPC Client
    logging.info("Request received")
    client = get_client(
        config.triton_url,
        config.triton_ssl,
        config.triton_root_certs,
        config.triton_private_key,
        config.triton_cert_chain,
    )
    logging.info("Loaded Triton client")
    try:
        load_model(
            client,
            config.model_name,
            config.model_version,
            config.triton_mode == "POLLING",
        )
        logging.info("Loaded model for inference")
        # Perform preprocessing
        # assumes RGB image and FP32 input
        if config.normalize_img:
            logging.info("Normalizing image")
            image = (
                image.astype(np.float32) - config.normalize_mean
            ) / config.normalize_std

        # Default shape of image is Width, Height, 3
        logging.info(f"Tensor Format: {config.img_tensor_format}")
        if config.img_tensor_format == TensorFormat.nhwc:
            # Convert to Height, Width, 3
            shape = [1, config.img_height, config.img_width, 3]
            image = np.transpose(image, (1, 0, 2))
        elif config.img_tensor_format == TensorFormat.nchw:
            # Convert to 3, Height, Width
            shape = [1, 3, config.img_height, config.img_width]
            image = np.transpose(image, (2, 1, 0))
        else:
            raise NotImplementedError("Format not supported yet")

        # Define expected input and output for Triton
        expected_input = tr.InferInput(config.input_layer, shape, "FP32")
        expected_input.set_data_from_numpy(np.expand_dims(image, 0))
        expected_output = tr.InferRequestedOutput(
            config.output_layer, class_count=config.num_labels
        )

        # Send Inference
        logging.info("Sending infer request to Triton")
        preds = client.infer(
            model_name=config.model_name,
            inputs=[expected_input],
            outputs=[expected_output],
            client_timeout=config.triton_client_timeout,
        ).as_numpy(config.output_layer)

        # Process output
        logging.info("Processing output")
        processed_preds = [
            result.decode("utf-8").split(":") for result in preds.tolist()[0]
        ]
        results = {}
        for confidence, _, class_name in processed_preds:
            results[class_name] = float(confidence)
        return results
    finally:
        # No matter what, unload model after prediction
        if config.triton_mode == "EXPLICIT" and client is not None:
            logging.info("Unloading model")
            unload_model(client, config.model_name)
