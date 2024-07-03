# import os
# os.environ["CURL_CA_BUNDLE"]=""
# Load model directly
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq

processor = AutoProcessor.from_pretrained("openai/whisper-large-v3")
model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-large-v3")
model.save_pretrained('whisper-large-v3-weights')