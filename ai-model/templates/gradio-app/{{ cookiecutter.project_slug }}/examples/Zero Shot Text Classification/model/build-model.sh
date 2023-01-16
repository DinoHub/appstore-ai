#!/bin/sh
# Use dockerfile to build model.pt
# First start by building container
echo $(pwd)
docker build . -t build-roberta-model:1.0 -f Dockerfile.build
docker run --gpus all --rm -v $(pwd):/app build-roberta-model:1.0
