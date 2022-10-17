
FROM tiencheng/inference-engine:latest

COPY requirements.txt .
RUN venv/bin/pip install -r requirements.txt
ARG PORT=4001
ARG HOSTNAME=0.0.0.0
ENV PORT=${PORT}
ENV HOSTNAME=${HOSTNAME}

EXPOSE ${PORT}
COPY . .
            
