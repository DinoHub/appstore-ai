#!/bin/sh
# Build image
docker build back-end -t aas-back-end:latest --build-arg ENV_STATE=prod
# docker push localhost:5001/aas-back-end:latest
docker build front-end -t aas-front-end:latest
# docker push localhost:5001/aas-front-end:latest
