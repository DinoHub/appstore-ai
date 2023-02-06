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
