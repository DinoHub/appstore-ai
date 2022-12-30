"""Jinja2 template environment for the project."""
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

template_env = Environment(
    loader=FileSystemLoader(
        Path(__file__).resolve().parent.parent.joinpath("templates")
    ),
    autoescape=select_autoescape(default=True),
)
