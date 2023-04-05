import logging

import gradio as gr
from predict import examples, inputs, outputs, predict

if __name__ == "__main__":
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s")
    app = gr.Interface(
        predict,
        inputs=inputs,
        outputs=outputs,
        title="yolo-v7",
        description="Inference service for AI App Store",
        examples=examples,
    )
    
    app.launch(
        server_name="0.0.0.0",
        server_port=8080,
        enable_queue=True,
    )
    
