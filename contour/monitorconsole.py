"""Console tool for Contour monitoring."""
import click

from contour.logfetch import get_statement_roots_for_address


@click.group()
def cli():
    """Utilities for Contour authority operators."""


@cli.command()
@click.argument('authority_address')
def roots(authority_address):
    """Get statement batch roots for an authority."""
    get_statement_roots_for_address(authority_address)
