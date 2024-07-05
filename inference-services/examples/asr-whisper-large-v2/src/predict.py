import librosa
import torch

from transformers import WhisperProcessor, WhisperForConditionalGeneration
from typing import Dict, List, Union

import gradio as gr
from config import config

inputs: Union[str, gr.inputs.Audio] = gr.inputs.Audio(source='upload', type='filepath')
outputs: str = 'text'

''' CPU/GPU Configuration'''
device = 'cuda' if torch.cuda.is_available() else 'cpu'

processor = WhisperProcessor.from_pretrained("/model/whisper-large-v2/")
model = WhisperForConditionalGeneration.from_pretrained("/model/whisper-large-v2/", use_safetensors=True).to(device)
model.config.forced_decoder_ids = None
print("Finished loading model")

def preprocess_audio(audio_path):
    # load an audio in
    audio_array = [librosa.load(path=audio_path, sr=16000)[0]]
    input_features = processor(audio_array, sampling_rate=16000, return_tensors='pt').input_features.to(device)
    return input_features

def predict(audio_path: str) -> str:
    input_features = preprocess_audio(audio_path)

    # generate token ids 
    predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription[0]