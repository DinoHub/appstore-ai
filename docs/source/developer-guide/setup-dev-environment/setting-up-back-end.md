# Setting Up Back-End

## Pre-requisites

Before setting up the back-end for development, you will need to have the following installed:

- [Python](https://www.python.org/downloads/) (version 3.8 or higher)
- [Poetry](https://python-poetry.org/docs/#installation)

See [Setting Up Development Tools](development-tools.md#installing-python) for more information on setting up your development environment.

## Setting Up MongoDB

Assuming you have MongoDB set up, you will need to start it up.

### Using Docker

If you are using the Docker Compose setup, you can start up MongoDB by running:

```bash
docker compose up -d mongodb
```

### Non-docker Setup

To install MongoDB locally without Docker, follow the instructions [here](https://docs.mongodb.com/manual/installation/)

Follow the instructions to install and start up MongoDB. You should be able to connect to the MongoDB instance at `mongodb://localhost:27017`.

## Setting Up MinIO

### Using Docker

If you are using the Docker Compose setup, you can start up MinIO by running:

```bash
docker compose up -d minio
```

### Non-docker Setup

To install Minio locally without Docker, follow the instructions [here](https://min.io/docs/minio/linux/operations/install-deploy-manage/deploy-minio-single-node-single-drive.html)

Once started, you should be able to connect to the MinIO API instance at `http://localhost:9000`. The console can be accessed at `http://localhost:9090`.

## Installing Dependencies

To install, change to the `back-end` directory and run:

```bash
python -m venv venv
source venv/bin/activate
poetry install
```

The core dependencies are listed in `back-end/pyproject.toml`. The key dependencies are:

- [FastAPI](https://fastapi.tiangolo.com/): a modern, fast (high-performance), web framework for building APIs with Python 3.6+ based on standard Python type hints.
- [Pydantic](https://pydantic-docs.helpmanual.io/): data validation and settings management using Python type hinting.
- [Motor](https://motor.readthedocs.io/en/stable/): an asynchronous Python driver for MongoDB.
- [Minio](https://docs.min.io/docs/python-client-quickstart-guide.html): a Python client for S3-compatible object storage.
- [ClearML](https://clear.ml/docs/docs/python_sdk/index.html): a Python client for ClearML.
- [Jinja2](https://jinja.palletsprojects.com/en/3.0.x/): a modern and designer-friendly templating language for Python.
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/): a Python library for parsing HTML and XML documents.
- [Kubernetes](https://kubernetes.io/docs/reference/using-api/client-libraries/): a Python client for Kubernetes.
- The core development dependencies are:
- [Pytest](https://docs.pytest.org/en/stable/): a testing framework for Python.
- [Hypothesis](https://hypothesis.readthedocs.io/en/latest/): a library for property-based testing.
- [Black](https://black.readthedocs.io/en/stable/): a Python code formatter.
- [isort](https://pycqa.github.io/isort/): a Python utility / library to sort imports.

## Setting up Environment Variables

Configuration for the app is done by dotenv files. The dotenv file is located in `back-end/src/config/.env`. If you do not have this file, you will need to create it as a copy of `back-end/src/config/.env.public` and fill in the values (as we do not want to commit the dotenv file to the repository to avoid leaking sensitive secrets, and thus we gitignored the .env file).

### Encryption and Decryption

To supply environment variables for CI, we encrypt the dotenv file using gpg (with a passphrase).

To encrypt the dotenv file, run the following in the config directory:

```bash
sh encrypt-env.sh <passphrase>
```

Substitute `<passphrase>` with the passphrase you want to use. But note that the Github repository stores the passphrase as a secret, so you will need to use the same passphrase as the one in the Github repository (or update the Github repository with the new passphrase).

To decrypt the dotenv file, run the following in the config directory:

```bash
sh decrypt-env.sh <passphrase>
```

### ClearML Credentials

The backend needs to be able to connect to ClearML for integration. To do this, you will need to set the following environment variables:

- `CLEARML_API_KEY`: the API key for your ClearML account
- `CLEARML_API_SECRET`: the API secret for your ClearML account
- `CLEARML_API_HOST`: the API host for your ClearML account

## Running the App

### Local (Non-docker) Setup

To run the app in development mode, run:

```bash
poe boot
```

This will start up the app on port 7070. You can access the app at `http://localhost:7070`.

### Docker Setup

Run the following command to start up the app:

```bash
docker compose up -d back-end
```

This starts up the app on port 8080. Currently hot-reloading is not supported, so you will need to restart the docker compose (which will rebuild the image) to see changes.
