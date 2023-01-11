#!/bin/sh
# Build image
docker build back-end -t aas-backend:1.0.5 --build-arg ENV_STATE=prod
# docker push localhost:5001/aas-back-end:latest
docker build front-end -t aas-frontend:1.0.5
# docker push localhost:5001/aas-front-end:latest

docker build ai-model/inference-engine -t inference-engine:gradio-v2.9.4
