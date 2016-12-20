import click

import btc
import tree
from localconfig import config


@click.group()
def cli():
    """Tools for Untrusted Proofs of Auditability."""


@cli.command()
@click.argument('source_directory')
@click.argument('output_file')
def buildtree(source_directory, output_file):
    """Build a merkle tree of items for auditing."""
    mt = tree.build_tree_from_directory(source_directory)
    mt_json = tree.export_tree_as_json(mt)

    filehandle = open(output_file, 'w')
    filehandle.write(mt_json)
    filehandle.close()

    click.echo("Merkle tree saved to output file.")


@cli.command()
@click.argument('key')
def btcimportkey(key):
    """Import a Bitcoin private key."""
    address = btc.import_key(key)
    click.echo("Key for address %s imported." % address)


@cli.command()
def btclistaddresses():
    """List Bitcoin addresses."""
    for address in btc.keys():
        click.echo(address)


@cli.command()
@click.argument('address')
@click.argument('input_file')
def btccommittree(address, input_file):
    """Commit a merkle tree to the Bitcoin blockchain."""