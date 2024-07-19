import logging

import gradio as gr
from config import BaseConfig
from predict import inputs, outputs, predict

if __name__ == "__main__":
    logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s")
    config = BaseConfig()

    app = gr.Interface(
        predict,
        inputs=inputs,
        outputs=outputs,
        title="Sample Model Inference Service",
        description="This is NOT the actual model inference service for this model card. <br> The model owner has yet to submit his/her model. <br><br> While waiting, you may type your name in the textbox, drag the slider, and then press the Submit button. <br> You should see a friendly greeting in the output box. Have fun!",
    )
    app.launch(
        server_name="0.0.0.0", server_port=config.port, enable_queue=True
    )

