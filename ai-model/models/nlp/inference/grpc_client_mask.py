import argparse
import numpy as np
import sys
from functools import partial
import os
import tritonclient
import tritonclient.grpc.model_config_pb2 as mc
import tritonclient.http as tritonhttp
from tritonclient.utils import triton_to_np_dtype
from tritonclient.utils import InferenceServerException
from transformers import XLMRobertaTokenizer
from scipy.special import softmax
from transformers import AutoTokenizer, AutoModelForMaskedLM
import torch


VERBOSE = False
# hypothesis for topic classification
input_name = ['input__0', 'input__1']
output_name = 'output__0'
def run_inference(premise, model_name='zst', url='127.0.0.1:8000', model_version='1'):
    triton_client = tritonhttp.InferenceServerClient(
        url=url, verbose=VERBOSE)
    model_metadata = triton_client.get_model_metadata(
        model_name=model_name, model_version=model_version)
    model_config = triton_client.get_model_config(
        model_name=model_name, model_version=model_version)    
    tokenizer = AutoTokenizer.from_pretrained('xlm-roberta-large')
    
    inputs = tokenizer(premise, return_tensors="pt",truncation=True,padding = 'max_length' )
    input_ids = np.array(inputs['input_ids'], dtype=np.int32)
    attention_mask = np.array(inputs['attention_mask'], dtype=np.int32)

    print('Tokens passed')
    input0 = tritonhttp.InferInput(input_name[0], (1,  512), 'INT32')
    input0.set_data_from_numpy(input_ids, binary_data=False)
    print('input 0 ok')
    input1 = tritonhttp.InferInput(input_name[1], (1, 512), 'INT32')
    input1.set_data_from_numpy(attention_mask, binary_data=False)
    print('input 1 ok')
    output = tritonhttp.InferRequestedOutput(output_name,  binary_data=False)
    print('return ok')
    response = triton_client.infer(model_name,
    model_version = model_version, inputs=[input0, input1], outputs=[output])
    print('inference ok')
    logits = response.as_numpy('output__0')
    logits = torch.Tensor(logits)
    mask_token_index = torch.where(inputs["input_ids"] == tokenizer.mask_token_id)[1]
    print(mask_token_index)
    mask_token_logits = logits[0, mask_token_index,:]
    print(mask_token_index)
    # Pick the [MASK] candidates with the highest logits
    top_5_tokens = torch.topk(mask_token_logits, 5, dim=1).indices[0].tolist()

    for token in top_5_tokens:
        print(f"'>>> {premise.replace(tokenizer.mask_token, tokenizer.decode([token]))}'")
# topic classification premises
if __name__ == '__main__':
    run_inference("I am a <mask> model.",'xlm_rob_large_mask')