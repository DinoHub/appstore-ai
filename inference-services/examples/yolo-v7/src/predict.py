from typing import Any, List, Optional, Union

from config import config

import yolov7
import numpy as np
import gradio.inputs as gr_inputs
import gradio.outputs as gr_outputs

inputs = [
    gr_inputs.Image(
        source=config.source,
        type="filepath"
    )
]
outputs = [gr_outputs.Image(label="Detected Objects")]


examples: Optional[Union[List[Any], List[List[Any]], str]] = [
    "/app/src/data/pexels-edward-jenner-4033148.jpg"
]

model = yolov7.load(config.model_weights, device=config.device)

def predict(image: np.ndarray) -> np.ndarray:
    results = model(image)
    rendered_ouput = results.render()[0]
    return rendered_ouput

