# Hello World
Example executor that does nothing

## How to Use
The Inference Engine is a FastAPI server 
which can be started by either one of these
methods:
- Locally: Running `main.py` (`python main.py`)
    - Note that you will have to install any requirements before running it
    - It is also recommended to set up a virtual environment for this
- Docker: Building a Docker Image (`make build_image`) and running it.

Once the server is running, there are a few ways to interact with the service:
- Swagger UI: FastAPI includes interactive API documentation through the `/docs` endpoint which can be used to send requests to the server
- HTTP Client: Any HTTP client can be used to make a request (e.g Postman, Hopscotch, Python requests library)

## How to Build/Contribute
### Structure
```
.
├── 🐍 process.py
├── 🐍 main.py
├── ⚙️ config.yaml
├── 📃 requirements.txt
├── 🐋 Dockerfile
├── 🧰 Makefile
├── 📃 .gitignore
└── 📃 .dockerignore
```

| File/Dir | Description |
|---|---|
| process.py | Contains the user prediction function |
| main.py | The code that registers the user prediction function and starts the server |
| config.yaml | Contains metadata about the engine as well as information defining endpoints |
| requirements.txt | Any additional python dependencies on top of those of the inference-engine library |
| Dockerfile | Dockerfile to build the engine |
| Makefile | Useful scripts to aid in development |
| .gitignore | Files for Git VCS to ignore. |
| .dockerignore | Files to ignore on Docker build | 

### Defining Requirements
#### Python Packages
By default, the following packages should already be installed:
- `fastapi`
- `tritonclient[grpc]`
- `numpy`

You may need to add on more packages, which you can do by adding them to the `requirements.txt` file.

For example,
```
Pillow==9.2.0
opencv-python-headless==4.6.0.66
```

#### Non-Python Packages
In the Dockerfile (which uses `python:3.9-slim` as a base), you can install any other dependencies you require.

### Input Schema
Type: TextIO

### Output Schema
Type: TextIO

### User Function
The user function (`predict`), found in `process.py`, is the main processing code that takes in some input data,
and is expected to process it and return output data in a pre-defined
interface. 

### Deployment
#### Building the Container
To build a docker container using the `Dockerfile`,
you can make use of the `Makefile` by running:
```bash
make build_image
```
This will build the image and tag it as ie-Hello World:v1`

#### Publishing the Image
This image can then be pushed to a container registry.
```bash
docker image tag ie-hello-world:v1 registry-host:registry-port/my-name/ie-hello-world:v1
docker image push registry-host:registry-port/my-name/ie-hello-world:v1
```

## FAQ
- Q: What is the default port and hostname?
    - A: Default port is 4000, default hostname is 0.0.0.0
- Q: Can this be changed?
    - A: There is no real need to change it, but it can be done. In the `Dockerfile`, you can override the `PORT` and `HOSTNAME` environment variable.
