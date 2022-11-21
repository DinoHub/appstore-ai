FROM python:3.9-slim

COPY requirements.txt .

RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install -Ur requirements.txt

COPY . .
CMD [ "python", "main.py" ]
