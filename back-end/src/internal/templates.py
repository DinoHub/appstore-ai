from pathlib import Path

from jinja2 import Environment, FileSystemLoader

template_env = Environment(
    loader=FileSystemLoader(
        Path(__file__).resolve().parent.parent.joinpath("templates")
    )
)
