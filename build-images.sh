#!/bin/sh
# Build image
docker build back-end -t aas-backend:latest --build-arg ENV_STATE=prod
# docker push localhost:5001/aas-back-end:latest
docker build front-end -t aas-frontend:latest
# docker push localhost:5001/aas-front-end:latest
