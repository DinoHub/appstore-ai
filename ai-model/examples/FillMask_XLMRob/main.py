import gradio as gr
import numpy as np
import tritonclient.grpc as tritongrpc
from scipy.special import softmax
from datetime import datetime
import os
from transformers import AutoTokenizer
import torch


def loadModel(
    model_name="mask_fill", model_version="1", url="127.0.0.1:8001", loading="POLLING"
):
    # establish connection to triton
    triton_client = tritongrpc.InferenceServerClient(url=url, verbose=VERBOSE)
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Connection')

    # load model in triton, not needed if mode = 'polling'
    if loading == "EXPLICIT":
        triton_client.load_model(model_name)
    if not triton_client.is_model_ready(model_name):
        print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] FAILED: Load Model')
    else:
        print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Load Model')

    # get model data
    model_metadata = triton_client.get_model_metadata(
        model_name=model_name, model_version=model_version
    )
    model_config = triton_client.get_model_config(
        model_name=model_name, model_version=model_version
    )
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] CONFIG: {model_config}')
    return triton_client


def unloadModel(triton_client, model_name="zst"):
    # unload model from triton server
    triton_client.unload_model(model_name)
    if triton_client.is_model_ready(model_name):
        print(
            f'\n[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] FAILED: Unload Model'
        )
    else:
        print(
            f'\n[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED : Unload Model'
        )


def run_inference(
    triton_client, premise="", model_name="zst", model_version="1", top_k=5
):

    print(f'\n[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PREMISE: {premise}')

    # tokenize inputs and format
    inputs = tokenizer(
        premise, return_tensors="pt", truncation=True, padding="max_length"
    )
    input_ids = np.array(inputs["input_ids"], dtype=np.int32)
    attention_mask = np.array(inputs["attention_mask"], dtype=np.int32)
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Tokenize')

    # insert inputs and output(s)
    input0 = tritongrpc.InferInput(input_name[0], (1, 512), "INT32")
    input0.set_data_from_numpy(input_ids)
    input1 = tritongrpc.InferInput(input_name[1], (1, 512), "INT32")
    input1.set_data_from_numpy(attention_mask)
    output = tritongrpc.InferRequestedOutput(output_name)
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Inputs/Outputs')

    # send inputs for inference and recieve output(s)
    response = triton_client.infer(
        model_name,
        model_version=model_version,
        inputs=[input0, input1],
        outputs=[output],
    )
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Inference')

    # format output(s)
    logits = response.as_numpy("output__0")
    result = np.copy(logits)
    logits = torch.Tensor(result)
    mask_token_index = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)[1]
    mask_token_logits = logits[0, mask_token_index, :]
    probs = softmax(mask_token_logits)
    top_k_probs = torch.topk(torch.Tensor(probs), top_k).values[0].tolist()
    top_k_tokens = torch.topk(torch.Tensor(probs), top_k).indices[0].tolist()
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Masks Filled\n')

    # display output(s)
    for x in range(len(top_k_tokens)):
        print(
            f"[{(datetime.now()).strftime('%d-%m-%Y %H:%M:%S')}] SEQUENCE: {premise.replace(tokenizer.mask_token, tokenizer.decode([top_k_tokens[x]]))}\n\t\t      SCORE: {round(top_k_probs[x]*100,2)}%"
        )

    return top_k_tokens, top_k_probs


try:
    # load tokeniser
    tokenizer = AutoTokenizer.from_pretrained("xlm-roberta-large")
    VERBOSE = False
    # set up input for triton
    input_name = ["input__0", "input__1"]
    output_name = "output__0"
    # get variables from env pass in Dockerfile
    MODEL_NAME = os.environ.get("MODEL_NAME", "xlm_rob_large_mask")
    MODEL_VERSION = os.environ.get("MODEL_VERSION", "1")
    TRITON_HOSTNAME = os.environ.get("TRITON_HOSTNAME", "127.0.0.1")
    TRITON_PORT = str(os.environ.get("TRITON_PORT", "8001"))
    TRITON_MODE = os.environ.get("TRITON_MODE", "EXPLICIT")
    TRITON_URL = f"{TRITON_HOSTNAME}:{TRITON_PORT}"
    HOSTNAME = os.environ.get("HOSTNAME", "127.0.0.1")
    # get Triton client and load model in Triton
    client = loadModel(MODEL_NAME, MODEL_VERSION, TRITON_URL, TRITON_MODE)

    def question_answer(premise, top_k):
        # run Masking inference in Triton server and return correct output
        top_k_tokens, top_k_probs = run_inference(
            client, premise, MODEL_NAME, MODEL_VERSION, int(top_k)
        )

        # format outputs for display
        styledOutput = ""
        for x in range(len(top_k_tokens)):
            styledOutput += f"{tokenizer.decode([top_k_tokens[x]])} ({round(top_k_probs[x]*100,2)}%)\n"
        return styledOutput.strip()

    with gr.Blocks() as demo:
        # styling for Gradio frontend
        premiseBox = gr.Textbox(
            placeholder="Text to mask...", label="Mask token: <mask>"
        )
        topKbox = gr.Number(value=5, label="Number of masks")

        comp_btn = gr.Button("Compute")

        output = gr.Textbox(
            label="Probabilities", placeholder="<Token> (<Probability of being true>)"
        )
        # call function that sends inputs for inference and formats outputs for  display
        comp_btn.click(fn=question_answer, inputs=[premiseBox, topKbox], outputs=output)

    if __name__ == "__main__":
        # launch Gradio frontend
        demo.launch(server_name=HOSTNAME)
except:
    # catch for errors and unload model in Triton
    # NOTE: This doesn't really work very well, some issues with SciPy/other packages causes complete crash when keyboard interrupting
    unloadModel(client, MODEL_NAME)
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] Exited Application')
