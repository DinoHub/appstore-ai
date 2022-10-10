import click

from .commands.new import new


# Create new inference engine
@click.group()
@click.version_option()
def cli():
    """Command line interface for Inference Engine."""
    pass


cli.add_command(new)


if __name__ == "__main__":
    cli()
