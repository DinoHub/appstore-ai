from importlib.metadata import version
import numpy as np
import sys
import tritonclient.http as tritonhttp
from tritonclient.utils import triton_to_np_dtype
from tritonclient.utils import InferenceServerException
from transformers import XLMRobertaTokenizer
from scipy.special import softmax
from transformers import AutoTokenizer
import torch
from datetime import datetime

# load tokeniser
tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-large')
VERBOSE = False

# set up inputs for triton server
input_name = ['input__0', 'input__1']
output_name = 'output__0'

def run_inference(premise, model_name='xlm_rob_large_mask', url='127.0.0.1:8001', model_version='1'):

    print(f'\n[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PREMISE: {premise}')

    # establish connection to triton
    triton_client = tritonhttp.InferenceServerClient(
        url=url, verbose=VERBOSE)
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Connection')

    # load model in triton, not needed if mode = 'polling'
    triton_client.load_model(model_name)
    if not triton_client.is_model_ready(model_name):
        print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] FAILED: Load Model')
        sys.exit(1) 
    else:
        print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Load Model')

    # get model data
    model_metadata = triton_client.get_model_metadata(
        model_name=model_name, model_version=model_version)
    model_config = triton_client.get_model_config(
        model_name=model_name, model_version=model_version)    
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] CONFIG: {model_config}')
    
    # tokenize inputs and format
    inputs = tokenizer(premise, return_tensors="pt",truncation=True,padding = 'max_length' )
    input_ids = np.array(inputs['input_ids'], dtype=np.int32)
    attention_mask = np.array(inputs['attention_mask'], dtype=np.int32)

    # insert inputs and output(s)
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Tokenize')
    input0 = tritonhttp.InferInput(input_name[0], (1,  512), 'INT32')
    input0.set_data_from_numpy(input_ids,binary_data= False)
    input1 = tritonhttp.InferInput(input_name[1], (1, 512), 'INT32')
    input1.set_data_from_numpy(attention_mask,binary_data= False)
    output = tritonhttp.InferRequestedOutput(output_name,binary_data= False)
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Inputs/Outputs')

    # send inputs for inference and recieve output(s)
    response = triton_client.infer(model_name,
    model_version = model_version, inputs=[input0, input1], outputs=[output])
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Inference')

    # format output(s)
    logits = response.as_numpy('output__0')
    logits = torch.Tensor(logits)
    mask_token_index = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)[1]
    mask_token_logits = logits[0, mask_token_index,:]
    top_5_tokens = torch.topk(mask_token_logits, 5, dim=1).indices[0].tolist()
    print(torch.topk(mask_token_logits, 5, dim=1))
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Masks Filled')

    # display outputs
    for token in top_5_tokens:
        print(f">>>\t {premise.replace(tokenizer.mask_token, tokenizer.decode([token]))}")

    # unload model from client
    triton_client.unload_model(model_name)
    if triton_client.is_model_ready(model_name):
        print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] FAILED: Unload Model')
        sys.exit(1)
    else:
        print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Unload Model')

if __name__ == '__main__':
    run_inference("The dog ran <mask>.",'xlm_rob_large_mask')