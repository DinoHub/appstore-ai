FROM python:3.9-slim as python-base

WORKDIR /app
# https://python-poetry.org/docs#ci-recommendations
ENV POETRY_VERSION=1.2.1
ENV POETRY_HOME=/opt/poetry
# ENV POETRY_VENV=./venv

# Tell Poetry where to place its cache and virtual environment
ENV POETRY_CACHE_DIR=/opt/.cache

# Create stage for Poetry installation
FROM python-base as poetry-base

# Creating a virtual environment just for poetry and install it with pip
RUN python3 -m venv venv \
    && venv/bin/pip install -U pip setuptools \
    && venv/bin/pip install poetry==${POETRY_VERSION}

# Create a new stage from the base python image
FROM python-base as app

# Copy Poetry to app image
COPY --from=poetry-base /app/venv ./venv

# Add Poetry to PATH
ENV PATH="${PATH}:venv/bin"


# Copy Dependencies
COPY poetry.lock pyproject.toml ./
RUN poetry export -f requirements.txt | venv/bin/pip install -r /dev/stdin

# [OPTIONAL] Validate the project is properly configured
RUN poetry check

# Install Dependencies
# RUN poetry install --no-interaction --no-cache --without dev

# Copy Application
COPY . /app

# Build application
RUN poetry build && venv/bin/pip install install dist/*.whl

# Predefine ENVs
ENV PORT=4001
ENV HOSTNAME=0.0.0.0

EXPOSE ${PORT}

CMD [ "venv/bin/python", "main.py" ]
