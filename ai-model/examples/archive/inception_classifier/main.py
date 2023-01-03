import logging
import os

import gradio as gr
import numpy as np
import tritonclient.grpc as tr
import yaml
from utils import load_model, unload_model

logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s")


def predict(img: np.ndarray):
    config = yaml.safe_load(open("config.yaml", "r"))
    model_name = config["model_name"]
    model_version = config["model_version"]
    triton_url = config["triton_url"]
    triton_mode = config["triton_mode"]
    polling = triton_mode == "POLLING"
    try:
        client = load_model(model_name, model_version, triton_url, polling)
        inputs = [tr.InferInput("input", [1, 299, 299, 3], "FP32")]
        inputs[0].set_data_from_numpy(
            np.expand_dims(img.astype(np.float32) / 127.5 - 1, 0)
        )
        outputs = [
            tr.InferRequestedOutput(
                "InceptionV3/Predictions/Softmax", class_count=1001
            )
        ]
        output = client.infer(
            model_name=model_name, inputs=inputs, outputs=outputs
        ).as_numpy("InceptionV3/Predictions/Softmax")
        output = list(
            map(
                lambda result: result.decode("utf-8").split(":"),
                output.tolist()[0],
            )
        )
        results = {}
        for confidence, class_id, class_name in output:
            results[class_name] = float(confidence)
    except tr.InferenceServerException as e:
        raise e
    finally:
        if not polling and client is not None:
            unload_model(client, model_name)
    return results


demo = gr.Interface(
    fn=predict,
    inputs=gr.inputs.Image([299, 299]),
    outputs=gr.outputs.Label(num_top_classes=10),
).queue()


demo.launch(server_port=int(os.environ.get("PORT", 8080)))
