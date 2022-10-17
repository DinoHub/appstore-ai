FROM tiencheng/inference-engine:latest

COPY requirements.txt .
RUN venv/bin/pip install -r requirements.txt

COPY . .
