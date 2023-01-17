import logging
from typing import Dict

import gradio.inputs as gr_inputs
import gradio.outputs as gr_outputs
from config import config
from transformers import pipeline

inputs = [
    gr_inputs.Textbox(placeholder="Text to classify", label="Text"),
    gr_inputs.Textbox(
        placeholder="Possible class names", label="Comma Separated Labels"
    ),
]
outputs = gr_outputs.Label(num_top_classes=config.top_k)
examples = [["Hello world", "greeting,insult"]]

classifier = pipeline(
    "zero-shot-classification", model=config.model_name, device=config.device
)


def predict(text: str, classes: str) -> Dict[str, float]:
    """Takes in a text and list of
    possible classes. Then outputs probability
    of each class

    Args:
        text (str): Text to classify
        classes (str): Possible classes

    Returns:
        Dict[str, float]: _description_
    """
    # Initialize Triton GRPC Client
    logging.info("Request received")
    res = classifier(text, classes)
    labels = res["labels"]
    scores = res["scores"]
    results = {label: score for label, score in zip(labels, scores)}
    return results
