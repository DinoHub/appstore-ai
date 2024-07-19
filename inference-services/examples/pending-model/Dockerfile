# FROM tiencheng/inference-engine:1.0.0-py3.9-gr3.16.1-cpu
# COPY requirements.txt .
# RUN pip install -r requirements.txt
# COPY . .
# CMD ["python", "src/app.py"]


FROM docker.io/library/python:3.10@sha256:817c0d8684087acb6d88f0f0951f9a541aa3e762302aa5e8f439d5d12edd48ad
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "src/app.py"]