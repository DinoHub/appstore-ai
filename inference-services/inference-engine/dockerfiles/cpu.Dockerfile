ARG PYTHON_VERSION=3.8
FROM python:${PYTHON_VERSION} as python-base

ARG GRADIO_VERSION=2.9.4
# Install Gradio
RUN pip install gradio==${GRADIO_VERSION}
