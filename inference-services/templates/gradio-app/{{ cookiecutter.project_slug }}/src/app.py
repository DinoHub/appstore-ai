import logging

import gradio as gr
from config import config
from predict import examples, inputs, outputs, predict

if __name__ == "__main__":
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s")
    app = gr.Interface(
        predict,
        inputs=inputs,
        outputs=outputs,
        title="{{ cookiecutter.project_name }}",
        description="{{ cookiecutter.short_description }}",
        examples=examples,
    )
    {% if cookiecutter.gradio_version == "v2.9.4" %}
    app.launch(
        server_name="0.0.0.0", server_port=config.port, enable_queue=True
    )
    {% else %}
    app.launch(
        server_name="0.0.0.0",
        server_port=config.port
    ).queue()
    {% endif %}
