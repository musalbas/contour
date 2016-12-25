import click


@click.group()
def cli():
    """Tools for Contour."""


@cli.command()
@click.argument('input_file')
def verifyinclusionproof(input_file):
    """Verify an inclusion proof."""
    pass
