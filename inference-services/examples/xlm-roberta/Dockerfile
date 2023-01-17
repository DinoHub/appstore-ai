FROM tiencheng/inference-engine:1.0.0-py3.9-gr2.9.4-cuda11.8-cudnn8.6
RUN pip install click
ENV TRANSFORMERS_CACHE=/workdir/.cache
COPY requirements.txt .
RUN pip install -r requirements.txt
# Cache model
ADD ./scripts/save-huggingface-cache.py ./scripts/save-huggingface-cache.py
RUN python ./scripts/save-huggingface-cache.py -m "joeddav/xlm-roberta-large-xnli" 
COPY . .
CMD ["python", "src/app.py"]
