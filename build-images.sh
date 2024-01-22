#!/bin/sh
# Build image
APP_VERSION=${1:-'1.1.0'}
DOCKER_USERNAME=<docker_username>
docker build back-end -t docker.io/$DOCKER_USERNAME/aas-backend:$APP_VERSION --build-arg ENV_STATE=prod
docker build front-end -t docker.io/$DOCKER_USERNAME/aas-frontend:$APP_VERSION

docker push docker.io/$DOCKER_USERNAME/aas-backend:$APP_VERSION
docker push docker.io/$DOCKER_USERNAME/aas-frontend:$APP_VERSION

echo "y" | docker system prune

