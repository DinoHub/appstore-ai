import librosa
import torch
import logging

from time import time

from transformers import WhisperProcessor, WhisperForConditionalGeneration
from typing import Dict, List

# # from run.modules import preprocess_text
# from modules import TextPostProcessingManager, WER, CER, MER, GetF1Score, GetConfusionMatrix, DataCollatorSpeechSeq2SeqWithPadding, load_huggingface_manifest_evaluation, prepare_dataset, prepare_dataset_clearml, get_confidence_score, extract_file_path_from_json, extract_duration_from_json

# Setup logging in a nice readable format
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)5s][%(asctime)s][%(name)s]: %(message)s',
    datefmt='%H:%M:%S'
)

device = 'cuda' if torch.cuda.is_available() else 'cpu'

processor = WhisperProcessor.from_pretrained("./model/whisper-large-v3")
model = WhisperForConditionalGeneration.from_pretrained("./model/whisper-large-v3", use_safetensors=True).to(device)
model.config.forced_decoder_ids = None
audio_filepath_1 = 'hello-46355.wav'

# load an audio in
start_time = time()
audio_array = [librosa.load(path=audio_filepath_1, sr=16000)[0]]
input_features = processor(audio_array, sampling_rate=16000, return_tensors='pt').input_features.to(device)

# generate token ids 
predicted_ids = model.generate(input_features)

transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

end_time = time()
time_taken = end_time - start_time

print(transcription)
print(f"Time taken: {time_taken:.5} s")