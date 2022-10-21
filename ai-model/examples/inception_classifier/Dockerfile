FROM python:3.9-slim 

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -Ur requirements.txt

ARG PORT=7860
ARG HOST=0.0.0.0
ENV GRADIO_SERVER_PORT=${PORT}
ENV GRADIO_SERVER_NAME=0.0.0.0
EXPOSE ${PORT}

COPY . .
CMD ["python", "main.py"]
