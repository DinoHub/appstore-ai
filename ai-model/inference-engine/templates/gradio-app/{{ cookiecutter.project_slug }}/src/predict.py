import logging
from typing import Any, List, Optional, Union

import gradio as gr

from .config import config

inputs: List[Union[str, gr.components.Component]] = []
outputs: List[Union[str, gr.components.Component]] = []
examples: Optional[Union[List[Any], List[List[Any]], str]] = None


def predict():
    raise NotImplementedError
