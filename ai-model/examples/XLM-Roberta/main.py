import logging
import os

import gradio as gr
import numpy as np
import tritonclient.grpc as tr
import yaml
from scipy.special import softmax
from transformers import XLMRobertaTokenizer
from utils import load_model, unload_model

logging.basicConfig(format="[%(asctime)s] %(levelname)s: %(message)s")


def send_inference(
    client: tr.InferenceServerClient,
    sentence: str,
    classes: str,
    model_name: str = "xlm_roberta_zsl",
    model_version: str = "1",
):
    # Tokenize Input
    tokenizer = XLMRobertaTokenizer.from_pretrained(
        "joeddav/xlm-roberta-large-xnli"
    )
    tokens = tokenizer.encode(
        sentence,
        classes,
        max_length=256,
        truncation=True,
        padding="max_length",
    )
    logging.info("Token")
    logging.info(tokens)

    tokens = np.array(tokens, dtype=np.int32)
    mask = tokens != 1
    mask = np.array(mask, dtype=np.int32)
    mask = mask.reshape(1, 256)
    tokens = tokens.reshape(1, 256)

    inputs = [
        tr.InferInput("input__0", (1, 256), "INT32"),
        tr.InferInput("input__1", (1, 256), "INT32"),
    ]
    inputs[0].set_data_from_numpy(tokens)
    inputs[1].set_data_from_numpy(mask)

    outputs = [tr.InferRequestedOutput("output__0")]

    response = client.infer(
        model_name=model_name,
        model_version=model_version,
        inputs=inputs,
        outputs=outputs,
    )

    # Process outputs
    logits = response.as_numpy("output__0")
    logging.warning("===========================")
    logging.warning(logits)
    print("============================================")
    print(logits)
    logits = np.asarray(logits, dtype=np.float32)
    logging.warning(logits)
    entail_contradiction_logits = logits[:, [0, 2]]
    probs = softmax(entail_contradiction_logits)
    logging.warning("prois")
    logging.warning(probs)

    # Probability that label supports the sentence
    true_prob = probs[:, 1].item() * 100

    logging.warning("true")
    logging.warning(true_prob)
    return true_prob


def main():
    config = yaml.safe_load(open("config.yaml", "r"))
    model_name = os.environ.get(
        "MODEL_NAME", config.get("model_name", "xlm_roberta_zsl")
    )
    model_version = os.environ.get(
        "MODEL_VERSION", config.get("model_version", "1")
    )
    triton_url = os.environ.get(
        "TRITON_URL", config.get("triton_url", "172.20.0.4")
    )
    triton_mode = os.environ.get(
        "TRITON_MODE", config.get("triton_mode", "POLLING")
    )

    client = load_model(
        model_name, model_version, triton_url, triton_mode == "POLLING"
    )

    def predict(premise, topic):
        topics = list(filter(None, topic.split(",")))
        output_list = []
        for topic in topics:
            output = send_inference(
                client, premise, topic.strip(), model_name, model_version
            )
            output_list.append([topic, output])
        output_list = sorted(output_list, key=lambda x: x[1], reverse=True)
        # Sort by confidence
        results = {}
        for output in output_list:
            results[output[0]] = output[1]
        return results

    demo = gr.Interface(
        fn=predict,
        inputs=[
            gr.Textbox(
                placeholder="Text to classify",
                label="Zero Shot Classification",
            ),
            gr.Textbox(
                placeholder="Possible class names",
                label="Possible class names (comma separated)",
            ),
        ],
        outputs=[gr.outputs.Label(num_top_classes=10)],
    )
    return demo


if __name__ == "__main__":
    demo = main()
    demo.launch(server_port=int(os.environ.get("PORT", 8080)))
