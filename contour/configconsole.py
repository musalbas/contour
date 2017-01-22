"""Console tool for Contour configuration."""
import click

from contour.localdata import config


@click.group()
def cli():
    """Utilities for Contour authority operators."""


@cli.command()
@click.argument('rpc_uri')
def btcrpc(rpc_uri):
    """Set the URI for the Bitcoin RPC interface."""
    config['btc_rpc_uri'] = rpc_uri
    config.write()

    click.echo("Bitcoin RPC URI set to %s." % rpc_uri)
