import logging
from typing import List, Union

import gradio as gr

from .config import config

inputs: List[Union[str, gr.components.Component]] = []
outputs: List[Union[str, gr.components.Component]] = []


def predict():
    raise NotImplementedError
