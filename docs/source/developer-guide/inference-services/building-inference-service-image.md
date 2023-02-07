# Building the Inference Service Image

In the future, we will move towards relying on putting everything in the Dockerfile (so not using the inference service image as base).

But, for now, the Cookiecutter template for inference service relies on the inference service image as base. This page will explain how to build the inference service image.

## Pre-requisites

You will need to have the following installed:

- [Docker](https://docs.docker.com/get-docker/)
- [Python 3.8](https://www.python.org/downloads/)

## Running the Build Script

We have a script that will attempt to build every possible combination of the inference service image. This script is located in the `inference-services/inference-engine` folder in the root of the repository. To run the script, run the following command inside that folder:

```bash
python build.py --repo <docker repository> --username <username> --password <password>
```

If it fails to push the images, run the command with the flag `--skip_push` to skip pushing the images. Then, manually push the images.
