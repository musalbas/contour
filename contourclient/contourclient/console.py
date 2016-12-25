"""Console application for Contour client."""

import click


@click.group()
def cli():
    """Tools for Contour."""


@cli.command()
@click.argument('proof_file')
def verifyinclusionproof(proof_file):
    """Verify an inclusion proof."""
    pass
