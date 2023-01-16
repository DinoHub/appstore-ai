import logging
from typing import Any, List, Optional, Union

from config import config
{% if cookiecutter.gradio_version == "v2.9.4" %}
from gradio.inputs import InputComponent
from gradio.outputs import OutputComponent

inputs: List[Union[str, InputComponent]] = ["text"]
outputs: List[Union[str, OutputComponent]] = ["text"]
{% else %}
import gradio as gr

inputs: List[Union[str, gr.components.Component]] = ["text"]
outputs: List[Union[str, gr.components.Component]] = ["text"]
{% endif %}

examples: Optional[Union[List[Any], List[List[Any]], str]] = None


def predict(name: str) -> str:
    # TODO: Implement this!
    return f"Hello {name}"
