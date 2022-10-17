import click

from .commands.new import new
from .core.engine import InferenceEngine
from .schemas.io import *


# Create new inference engine
@click.group()
@click.version_option()
def cli():
    """Command line interface for Inference Engine."""
    pass


cli.add_command(new)
