import logging
from typing import Any, List, Optional, Union

from config import config
from gradio.inputs import InputComponent
from gradio.outputs import OutputComponent

inputs: List[Union[str, InputComponent]] = ["text"]
outputs: List[Union[str, OutputComponent]] = ["text"]
examples: Optional[Union[List[Any], List[List[Any]], str]] = None


def predict(name: str) -> str:
    # TODO: Implement this!
    return f"Hello {name}"
