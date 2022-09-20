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
R_tokenizer = XLMRobertaTokenizer.from_pretrained('joeddav/xlm-roberta-large-xnli')
VERBOSE = False
# hypothesis for topic classification

input_name = ['input__0', 'input__1']
output_name = 'output__0'
def run_inference(premise,topic, model_name='zst', url='127.0.0.1:8000', model_version='1'):
    topic = topic
    triton_client = tritonhttp.InferenceServerClient(
        url=url, verbose=VERBOSE)
    model_metadata = triton_client.get_model_metadata(
        model_name=model_name, model_version=model_version)
    model_config = triton_client.get_model_config(
        model_name=model_name, model_version=model_version)
    # I have restricted the input sequence length to 256
    input_ids = R_tokenizer.encode(premise, topic, max_length=256, 
    truncation=True, padding='max_length')
    input_ids = np.array(input_ids, dtype=np.int32)
    
    mask = input_ids != 1
    mask = np.array(mask, dtype=np.int32)
    
    mask = mask.reshape(1, 256) 
    input_ids = input_ids.reshape(1, 256)
    input0 = tritonhttp.InferInput(input_name[0], (1,  256), 'INT32')
    input0.set_data_from_numpy(input_ids, binary_data=False)
    input1 = tritonhttp.InferInput(input_name[1], (1, 256), 'INT32')
    input1.set_data_from_numpy(mask, binary_data=False)
    output = tritonhttp.InferRequestedOutput(output_name,  binary_data=False)
    response = triton_client.infer(model_name,
    model_version=model_version, inputs=[input0, input1], outputs=[output])
    logits = response.as_numpy('output__0')
    logits = np.asarray(logits, dtype=np.float32)
# we throw away "neutral" (dim 1) and take the probability of
    # "entailment" (2) as the probability of the label being true 
    entail_contradiction_logits = logits[:,[0,2]]
    probs = softmax(entail_contradiction_logits)
    true_prob = probs[:,1].item() * 100
    print(f'Probability that the label is true: {true_prob:0.2f}%')
# topic classification premises
if __name__ == '__main__':
    run_inference("Somewhere something incredible is waiting to be known"
    ,'This text is about space and cosmos','xlm_roberta_zsl')