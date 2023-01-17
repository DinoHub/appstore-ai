#!/bin/sh
# Build image
APP_VERSION=1.0.6
docker build back-end -t aas-backend:{APP_VERSION} --build-arg ENV_STATE=prod
docker build front-end -t aas-frontend:{APP_VERSION}
