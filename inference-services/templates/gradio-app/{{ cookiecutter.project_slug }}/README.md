# {{cookiecutter.project_name}}

{{cookiecutter.short_description}}

## Build
To build the docker container, run
```sh
make build
```

### Push to Registry
To push the image to a registry, first build the image, then run
```sh
docker tag {{ cookiecutter.project_slug }}:{{ cookiecutter.version }} <REGISTRY>/<REPO>/{{ cookiecutter.project_slug }}:{{ cookiecutter.version }}
```

If not logged in to the registry, run
```sh
docker login -u <USERNAME> -p <PASSWORD> <REGISTRY>
```

Then, push the tagged image to a registry
```sh
docker push <REGISTRY>/<REPO>/{{ cookiecutter.project_slug }}:{{ cookiecutter.version }}
```

## Run Locally
To run the Gradio application locally, run the following
```sh
make dev
```

## Deploy
First, make sure your image is pushed to the registry.

### Deployment on AI App Store
Check out the AI App Store documentation for full details, but in general:
1. Create/edit a model card
2. Pass the docker image URI (e.g `<REGISTRY>/<REPO>/{{ cookiecutter.project_slug }}:{{ cookiecutter.version }}`) when creating/editing the inference service

### Other Deployment Options
There are other potential deployment options, including:
- Google Cloud Run
- AWS Fargate
- Red Hat Openshift Serverless