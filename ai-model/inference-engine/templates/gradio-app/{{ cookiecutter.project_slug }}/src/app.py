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
    app.launch(server_port=config.port, enable_queue=True)
