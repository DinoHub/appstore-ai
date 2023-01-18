import logging
from typing import Any, List, Optional, Union

import gradio as gr
from config import config

inputs: List = ["text"]
outputs: List = ["text"]
examples: Optional[Union[List[Any], List[List[Any]], str]] = None


def predict(name: str) -> str:
    # TODO: Implement this!
    return f"{config.message}: {name}"
