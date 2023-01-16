import logging
from typing import Dict, Optional

{% if cookiecutter.gradio_version == "v2.9.4" %}
import gradio.inputs as gr_inputs
import gradio.outputs as gr_outputs
{% else %}
import gradio as gr
{% endif %}
import numpy as np
import tritonclient.grpc as tr
from config import config
from transformers import XLMRobertaTokenizer
from triton_utils import get_client, load_model, unload_model

{% if cookiecutter.gradio_version == "v2.9.4" %}
inputs = [
    gr_inputs.Textbox(placeholder="Text to classify", label="Text"),
    gr_inputs.Textbox(
        placeholder="Possible class names", label="Comma Separated Labels"
    ),
]
outputs = gr_outputs.Label(num_top_classes=config.top_k)
{% else %}
inputs = [
    gr.Text(placeholder="Text to classify", label="Text"),
    gr.Text(
        placeholder="Possible class names", label="Comma Separated Labels"
    ),
]
outputs = gr.Label(num_top_classes=config.top_k)
{% endif %}
examples = [["Hello world", "greeting,insult"]]

tokenizer = XLMRobertaTokenizer.from_pretrained(
    "joeddav/xlm-roberta-large-xnli"
)  # TODO: Cache vocab file first to improve cold start time


def softmax(x: np.ndarray, axis: Optional[int] = None) -> np.ndarray:
    """Softmax activation

    :param x: Logits
    :type x: np.ndarray
    :param axis: _description_, defaults to None
    :type axis: Optional[int], optional
    :return: _description_
    :rtype: np.ndarray
    """
    x_max = np.amax(x, axis=axis, keepdims=True)
    exp_x_shifted = np.exp(x - x_max)
    return exp_x_shifted / np.sum(exp_x_shifted, axis=axis, keepdims=True)


def get_probability(logits: np.ndarray) -> float:
    """Get probabilty that a text is
    of a proposed class

    :param logits: Model logits
    :type logits: np.ndarray
    :return: Probability (0-1)
    :rtype: float
    """
    logits = logits.astype(np.float32)
    # Model gives prob of 2 classes (neutral, entailment)
    # entailment is the probability that a statement supports
    # a hypothesis (e.g hypo = This example is {label})
    entail_contradiction_logits = logits[:, [0, 2]]
    probs = softmax(entail_contradiction_logits)
    true_prob = probs[:, 1].item()  # Entailment prob
    return true_prob


def predict(text: str, classes: str) -> Dict[str, float]:
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
        # Tokenize Input
        classes_list = classes.strip().split(",")
        results = {}
        text_input = tr.InferInput("input__0", [1, 256], "INT32")
        mask_input = tr.InferInput("input__1", [1, 256], "INT32")
        expected_output = tr.InferRequestedOutput("output__0")
        for possible_label in classes_list:
            hypothesis = f"This example is ${possible_label}"
            token_ids = tokenizer.encode(
                text,
                hypothesis,
                max_length=256,
                padding="max_length",
                truncation=True,
            )
            token_ids = np.array(token_ids, dtype=np.int32)
            mask = token_ids != 1
            mask = np.array(mask, dtype=np.int32)
            mask = mask.reshape(1, 256)
            token_ids = token_ids.reshape(1, 256)

            # Set data
            text_input.set_data_from_numpy(token_ids)
            mask_input.set_data_from_numpy(mask)

            # Send Inference
            logging.info("Sending infer request to Triton")
            logits = client.infer(
                model_name=config.model_name,
                inputs=[text_input, mask_input],
                outputs=[expected_output],
                client_timeout=config.triton_client_timeout,
            ).as_numpy("output__0")
            prob = get_probability(logits)
            results[possible_label] = prob
        return results
    finally:
        # No matter what, unload model after prediction
        if config.triton_mode == "EXPLICIT" and client is not None:
            logging.info("Unloading model")
            unload_model(client, config.model_name)
