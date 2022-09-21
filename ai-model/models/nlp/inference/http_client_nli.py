import argparse
import numpy as np
import sys
from functools import partial
import os
import tritonclient
import tritonclient.http as tritonhttp
from tritonclient.utils import triton_to_np_dtype
from tritonclient.utils import InferenceServerException
from transformers import XLMRobertaTokenizer
from scipy.special import softmax
from datetime import datetime

# load tokeniser
R_tokenizer = XLMRobertaTokenizer.from_pretrained('joeddav/xlm-roberta-large-xnli')
VERBOSE = False

# set up input for triton
input_name = ['input__0', 'input__1']
output_name = 'output__0'

def run_inference(premise = '',topic = '', model_name='zst', url='127.0.0.1:8000', model_version='1'):
    topic = topic
    print(f'\n[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PREMISE: {premise}')
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] TOPIC: {topic}')

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

    # tokenize input
    input_ids = R_tokenizer.encode(premise, topic, max_length=256, 
    truncation=True, padding='max_length')
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Tokenize')

    # format inputs
    input_ids = np.array(input_ids, dtype=np.int32)
    mask = input_ids != 1
    mask = np.array(mask, dtype=np.int32)
    mask = mask.reshape(1, 256) 
    input_ids = input_ids.reshape(1, 256)

    # insert inputs and output(s)
    input0 = tritonhttp.InferInput(input_name[0], (1,  256), 'INT32')
    input0.set_data_from_numpy(input_ids,binary_data= False)
    input1 = tritonhttp.InferInput(input_name[1], (1, 256), 'INT32')
    input1.set_data_from_numpy(mask,binary_data= False)
    output = tritonhttp.InferRequestedOutput(output_name,binary_data= False)
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Inputs/Outputs')

    # send inputs for inference and recieve output(s)
    response = triton_client.infer(model_name,
    model_version=model_version, inputs=[input0, input1], outputs=[output])
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Inference')

    # format output(s)
    logits = response.as_numpy('output__0')
    logits = np.asarray(logits, dtype=np.float32)
    entail_contradiction_logits = logits[:,[0,2]]
    probs = softmax(entail_contradiction_logits)
    true_prob = probs[:,1].item() * 100
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED: Probability')

    # display outputs
    print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] LABEL IS TRUE: {true_prob:0.2f}%')
    
    # unload model from triton server
    triton_client.unload_model(model_name)
    if triton_client.is_model_ready(model_name):
        print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] FAILED: Unload Model')
        sys.exit(1)
    else:
        print(f'[{(datetime.now()).strftime("%d-%m-%Y %H:%M:%S")}] PASSED : Unload Model')
    


if __name__ == '__main__':
    run_inference("The nebulas dance divinely in our heavenly skies"
    ,'This text is about space and cosmos','xlm_roberta_zsl')