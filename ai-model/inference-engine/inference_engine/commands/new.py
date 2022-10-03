from pathlib import Path

import click
from inference_engine.schemas.media_types import media_type

from ..schemas.io import HAS_MEDIA
from ..schemas.io import __all__ as AVAILABLE_IO_TYPES
from ..schemas.media_types import media_type
from ..utils.generate_engine import (
    generate_engine,
    generate_metadata_yml,
    generate_user_function,
)


@click.group()
def new():
    pass


@new.command()
@click.option(
    "--path",
    "-p",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    prompt="Enter directory to make new engine in:",
    default=Path.cwd(),
)
@click.option("--name", "-n", prompt="Enter name of engine:")
@click.option("--version", "-v", prompt=True, default="v1")
@click.option("--description", "-d", prompt=True)
@click.option("--author", "-a", prompt=True)
@click.option(
    "--input_schema",
    "-i",
    type=click.Choice(
        AVAILABLE_IO_TYPES,
    ),
    prompt=True,
)
@click.option(
    "--output_schema",
    "-o",
    type=click.Choice(
        AVAILABLE_IO_TYPES,
    ),
    prompt=True,
)
def engine(
    path: Path,
    name: str,
    version: str,
    description: str,
    author: str,
    input_schema: str,
    output_schema: str,
):
    # Get additional info
    # If output has media, ask for MIME type
    if output_schema in HAS_MEDIA:
        output_mime = click.prompt(
            "Select MIME Type of Output Media:",
            type=click.Choice(
                [
                    media_type.attr
                    for attr in media_type.__dict__.keys()
                    if not attr.startswith("_")
                ]
            ),
        )
    else:
        output_mime = None
    # Generate metadata file
    click.echo("Generating metadata")
    generate_metadata_yml(
        base_dir=path,
        name=name,
        version=version,
        description=description,
        author=author,
    )

    # Create engine.py
    click.echo("Generating files")
    generate_user_function(
        base_dir=path, input_schema=input_schema, output_schema=output_schema
    )

    # Generate main func
    generate_engine(
        base_dir=path,
        input_schema=input_schema,
        output_schema=output_schema,
        metadata_path=path.joinpath("meta.yaml"),
        media_type=output_mime,
    )
    click.echo(f"Successfully generated template at {str(path.absolute())}")
