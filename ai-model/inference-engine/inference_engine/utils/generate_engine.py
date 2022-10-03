from pathlib import Path
from typing import Optional, Union

import yaml


def generate_metadata_yml(
    base_dir: Union[str, Path],
    name: str,
    version: str,
    description: str,
    author: str,
    **kwargs,
):
    metadata = {
        "name": name,
        "version": version,
        "description": description,
        "author": author,
        **kwargs,
    }
    with open(base_dir.joinpath("meta.yaml"), "w") as f:
        yaml.dump(metadata, f)


def generate_user_function(
    base_dir: Union[str, Path], input_schema: str, output_schema: str
):
    with open(base_dir.joinpath("process.py"), "w") as f:
        f.write(
            f"""
from inference_engine import {input_schema}, {output_schema}


def predict(data: {input_schema}) -> {output_schema}:
    # TODO: Process inputs
    
    return {output_schema
    }() # TODO: Return data here
            """
        )


def generate_engine(
    base_dir: Union[str, Path],
    input_schema: str,
    output_schema: str,
    metadata_path: Union[str, Path],
    media_type: Optional[str],
):
    with open(base_dir.joinpath("main.py"), "w") as f:
        f.write(
            f"""
from inference_engine import InferenceEngine, {input_schema}, {output_schema}
from process import predict


engine = InferenceEngine.from_yaml("{metadata_path.relative_to(base_dir)}")
engine.entrypoint(
    predict, {input_schema}, {output_schema}, media_type="{media_type}"
)
if __name__ == "__main__":
    engine.serve()
            """
        )
    with open(base_dir.joinpath("Dockerfile"), "w") as f:
        f.write(
            f"""
FROM inference_engine:latest

COPY requirements.txt .
RUN venv/bin/pip install -r requirements.txt
ARG PORT=4001
ARG HOSTNAME=0.0.0.0
ENV PORT=${{PORT}}
ENV HOSTNAME=${{HOSTNAME}}

EXPOSE ${{PORT}}
COPY . .
            """
        )
    with open(base_dir.joinpath("requirements.txt"), "w") as f:
        f.write("")
