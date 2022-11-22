import logging
import os

import gradio as gr

from .config import config

logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s")


def main():
    raise NotImplementedError


if __name__ == "__main__":
    {%- if cookiecutter.example_task == "Image Classification" -%}
    inputs = "image"
    outputs = "label"
    {%- elif cookiecutter.example_task == "Fill-Mask" -%}
    inputs = "text"
    outputs = "text"
    {%- else -%}
    inputs = None
    outputs = None
    {% endif %}

    app = gr.Interface(
        main,
        inputs=inputs,
        outputs=outputs,
        title="{{ cookiecutter.project_name }}",
        description="{{ cookiecutter.short_description }}",
    )
    app.queue().launch(server_port=config.port)
