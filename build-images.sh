#!/bin/sh
# Build image
FRONTEND_APP_VERSION=${1:-'1.2.2'}
BACKEND_APP_VERSION=${1:-'1.2.0'}

DOCKER_USERNAME=<docker_username>

docker build back-end -t docker.io/$DOCKER_USERNAME/aas-backend:$BACKEND_APP_VERSION --build-arg ENV_STATE=prod
docker build front-end -t docker.io/$DOCKER_USERNAME/aas-frontend:$FRONTEND_APP_VERSION

docker push docker.io/$DOCKER_USERNAME/aas-backend:$BACKEND_APP_VERSION
docker push docker.io/$DOCKER_USERNAME/aas-frontend:$FRONTEND_APP_VERSION

echo "y" | docker system prune

