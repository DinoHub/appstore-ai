from pathlib import Path
from typing import Optional, Union

from jinja2 import Environment, FileSystemLoader

template_env = Environment(
    loader=FileSystemLoader(
        Path(__file__).resolve().parent.parent.joinpath("templates/v1")
    ),
)


def generate_metadata_yml(
    base_dir: Union[str, Path],
    name: str,
    version: str,
    description: str,
    author: str,
    input_schema: str,
    output_schema: str,
):
    template = template_env.get_template("config.yaml.j2")
    template = template.render(
        name=name,
        description=description,
        author=author,
        version=version,
        input_schema=input_schema,
        output_schema=output_schema,
        tag_name=generate_tag_name(name, version),
    )
    with open(base_dir.joinpath("config.yaml"), "w") as f:
        f.write(template)


def generate_readme(
    base_dir: Union[str, Path],
    name: str,
    version: str,
    description: str,
    author: str,
    input_schema: str,
    output_schema: str,
):
    template = template_env.get_template("README.md.j2")
    template = template.render(
        name=name,
        description=description,
        author=author,
        version=version,
        input_schema=input_schema,
        output_schema=output_schema,
        tag_name=generate_tag_name(name, version),
    )
    with open(base_dir.joinpath("README.md"), "w") as f:
        f.write(template)


def generate_makefile(
    base_dir: Union[str, Path],
    name: str,
    version: str,
):
    template = template_env.get_template("Makefile.j2")
    template = template.render(tag_name=generate_tag_name(name, version))
    with open(base_dir.joinpath("Makefile"), "w") as f:
        f.write(template)


def generate_tag_name(name: str, version: str) -> str:
    # Remove alphanumeric
    name = "-".join(
        [
            "".join(char for char in word if char.isalnum())
            for word in name.split(" ")
        ]
    ).lower()
    version = "-".join(
        [
            "".join(char for char in word if char.isalnum())
            for word in version.split(" ")
        ]
    ).lower()
    tag_name = "ie-" + name + ":" + version
    tag_name = tag_name[:128]  # Docker limits max length
    return tag_name


def generate_user_function(
    base_dir: Union[str, Path], input_schema: str, output_schema: str
):
    template = template_env.get_template("process.py.j2")
    template = template.render(
        input_schema=input_schema, output_schema=output_schema
    )
    with open(base_dir.joinpath("process.py"), "w") as f:
        f.write(template)


def generate_engine(
    base_dir: Union[str, Path],
    input_schema: str,
    output_schema: str,
    metadata_path: Union[str, Path],
):
    template = template_env.get_template("main.py.j2")
    template = template.render(
        input_schema=input_schema,
        output_schema=output_schema,
        metadata_yaml=metadata_path.relative_to(base_dir),
    )
    with open(base_dir.joinpath("main.py"), "w") as f:
        f.write(template)
    for file in (
        "Dockerfile",
        ".gitignore",
        ".dockerignore",
        "requirements.txt",
    ):
        text = template_env.get_template(file).render()
        with open(base_dir.joinpath(file), "w") as f:
            f.write(text)
