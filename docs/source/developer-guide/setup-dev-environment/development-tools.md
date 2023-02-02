# Setting Up Development Tools

## Overview

This page describes how to set up the development dependencies needed to start contributing to the project.

### Operating Systems

We suggest using a Linux distribution for development. We have tested the following distributions:

- Fedora Workstation
- Pop!\_OS
- Ubuntu

Most instructions will assume you are using a Linux distribution. If you are using a different operating system, you may need to adapt the instructions.

### Languages

- Python 3.8 or higher
- Typescript (Node.js 16 or higher)

### Tools

- [Poetry](https://python-poetry.org/docs/#installation)
- [Node Package Manager](https://nodejs.org/en/download/package-manager/)
- [Kubernetes](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- [Docker](https://docs.docker.com/get-docker/)
- [Helm](https://helm.sh/docs/intro/install/)
- [Skaffold](https://skaffold.dev/docs/install/)
- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [MongoDB](https://docs.mongodb.com/manual/installation/)
- [MinIO](https://docs.min.io/docs/minio-quickstart-guide.html)

## Dev Container

This project uses [VS Code Remote Containers](https://code.visualstudio.com/docs/remote/containers) to provide a consistent development environment. This is the recommended way to develop for this project. If you are using VS Code, you can open the project in a container by opening the project in VS Code and clicking the "Reopen in Container" button in the lower left corner of the window.

It will take a while to build the container the first time you open the project in a container. After the container is built, you can open a terminal in the container by clicking the "Open a Terminal" button in the lower left corner of the window.

Note that you would need [Docker](https://docs.docker.com/get-docker/) installed on your machine to use this feature as well as the [Remote - Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension for VS Code.

If you are not using the dev container, you will need to install the dependencies listed below.

## Installing Python

The suggested version of Python is 3.8 or higher. We recommend using [pyenv](https://github.com/pyenv/pyenv) to install Python, as it manages different versions of Python, allowing you to easily select which version of Python to use.

Other options include using your operating system's package manager or using a Python distribution such as [Anaconda](https://www.anaconda.com/products/individual).

## Installing Poetry

Poetry is a dependency manager for Python. It is used to manage the Python dependencies for the project. It is also used to create virtual environments for the project. We recommend using the [recommended installation method](https://python-poetry.org/docs/#installation) for your operating system.

## Installing Node.js

The suggested version of Node.js is the LTS version. We recommend using [nvm](https://github.com/nvm-sh/nvm) to install Node.js, as it manages different versions of Node.js, allowing you to easily select which version of Node.js to use.

## Installing Docker

Docker is used to build and run the project, as well as to run the database and object storage. We recommend using the [recommended installation method](https://docs.docker.com/get-docker/) for your operating system.

## Installing Kubectl

Kubectl is used to interact with Kubernetes. We recommend using the [recommended installation method](https://kubernetes.io/docs/tasks/tools/install-kubectl/) for your operating system.

## Installing Helm

Helm is a Kubernetes package manager. It is needed as when doing K8S deployment, we will use Helm to install dependencies (e.g MongoDB), as well as deploy the app. We recommend using the [recommended installation method](https://helm.sh/docs/intro/install/) for your operating system.

## Installing Kind

Kind is a tool for running local Kubernetes clusters using Docker container nodes. It is used to run the Kubernetes cluster locally. We recommend using the [recommended installation method](https://kind.sigs.k8s.io/docs/user/quick-start/) for your operating system.

## Installing Skaffold

Skaffold is a tool that facilitates continuous development for Kubernetes applications. It is used to build and deploy the project to the Kubernetes cluster. We recommend using the [recommended installation method](https://skaffold.dev/docs/install/) for your operating system.

## Installing MongoDB

### Docker Installation

The repository contains a Docker Compose file that can be used to run MongoDB. To run MongoDB using Docker Compose, run the following command from the root of the repository:

```bash
docker compose up -d mongodb
```

### Manual Installation

You can also install MongoDB manually. We recommend using the [recommended installation method](https://docs.mongodb.com/manual/installation/) for your operating system.

## Installing MinIO

### Docker Installation

The repository contains a Docker Compose file that can be used to run MinIO. To run MinIO using Docker Compose, run the following command from the root of the repository:

```bash
docker compose up -d minio
```

### Manual Installation

You can also install MinIO manually. We recommend using the [recommended installation method](https://docs.min.io/docs/minio-quickstart-guide.html) for your operating system.

## Installing Pre-Commit

Pre-commit is a tool that can be used to run a set of checks before committing code. It can be used to ensure that code is formatted correctly, that it passes linting checks, and that it passes tests. It can also be used to automatically format code and fix linting errors.

As pre-commit is a Python package, we recommend using [pipx](https://pipxproject.github.io/pipx/) to install it. Pipx is a tool that allows you to install Python packages in isolated environments, allowing you to easily install and manage Python packages. To install pipx, run the following command:

```bash
python3 -m pip install --user pipx
```

Then, to install pre-commit, run the following command:

```bash
pipx install pre-commit
```

To install the pre-commit hooks, run the following command from the root of the repository:

```bash
pre-commit install
```

The pre-commit hooks will run automatically when you commit code. If you would like to run the pre-commit hooks manually, run the following command from the root of the repository:

```bash
pre-commit run --all-files
```

In the case that you would like to skip the pre-commit hooks, you can use the `--no-verify` flag when committing code. For example:

```bash
git commit -m "Commit message" --no-verify
```

## VS Code Extensions

The repository contains a list of recommended VS Code extensions. You can install these extensions by opening the Command Palette (Ctrl+Shift+P) and running the "Extensions: Show Recommended Extensions" command.
