from binascii import hexlify

import click

import btc
import tree
from localconfig import config


@click.group()
def cli():
    """Tools for Contour."""


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
    fh = open(input_file)
    mt = tree.import_tree_from_json(fh.read())
    mt.build()
    fh.close()

    root = mt.get_chain(0)[-1][0]
    key = btc.get_key(address)
    tx = btc.send_op_return_tx(key, root)

    click.echo("Transaction committing tree %s sucessfully broadcast." % hexlify(root).decode('utf8'))
    click.echo("Transaction hash: %s." % tx.id())
