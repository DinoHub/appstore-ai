FROM ghcr.io/dinohub/appstore-ai-inference-engine:main

COPY requirements.txt .
RUN venv/bin/pip install -r requirements.txt

COPY . .
