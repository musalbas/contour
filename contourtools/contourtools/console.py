"""Console application for Contour tools."""

from binascii import hexlify
import json

import click
from pycoin.tx import Tx

from contourtools import btc
from contourtools import tree
from contourtools.localconfig import config


@click.group()
def cli():
    """Tools for Contour."""


@cli.command()
@click.argument('source_directory')
@click.argument('output_file')
def buildbatch(source_directory, output_file):
    """Build metadata for batch of files to commit."""
    mt = tree.build_tree_from_directory(source_directory)
    mt_json = tree.export_tree_as_json(mt)

    filehandle = open(output_file, 'w')
    filehandle.write(mt_json)
    filehandle.close()

    click.echo("Batch metadata saved to output file.")


@cli.command()
@click.argument('key')
def btcimportkey(key):
    """Import a Bitcoin private key."""
    address = btc.import_key(key).address()
    click.echo("Key for address %s imported." % address)


@cli.command()
def btclistaddresses():
    """List Bitcoin addresses."""
    for address in btc.keys():
        click.echo(address)


@cli.command()
@click.argument('address')
@click.argument('batch_file')
def btccommittree(address, batch_file):
    """Commit a batch metadata file to the Bitcoin blockchain."""
    filehandle = open(batch_file)
    batch_file_data = filehandle.read()
    filehandle.close()

    mt = tree.import_tree_from_json(batch_file_data)
    mt.build()

    key = btc.get_key(address)

    tx = tree.btc_commit_tree(mt, key)

    mt_json = tree.export_tree_as_json(mt)
    filehandle = open(input_file, 'w')
    filehandle.write(mt_json)
    filehandle.close()

    click.echo("Transaction to commit batch %s sucessfully broadcast." % hexlify(root).decode('utf8'))
    click.echo("Transaction hash: %s." % tx.id())
    click.echo()
    click.echo("Transaction data added to batch metadata file.")


@cli.command()
@click.argument('batch_file')
def btcattachblock(batch_file):
    """After confirmation, attach block and merkle path details to a committed batch metadata file."""
    filehandle = open(batch_file)
    batch_file_data = filehandle.read()
    filehandle.close()

    mt = tree.import_tree_from_json(batch_file_data)
    mt.build()

    click.echo("Downloading block for batch %s..." % hexlify(mt.root.val).decode())
    tree.btc_attach_block(mt)

    mt_json = tree.export_tree_as_json(mt)
    filehandle = open(batch_file, 'w')
    filehandle.write(mt_json)
    filehandle.close()

    click.echo("Block path data added to input file.")


@cli.command()
@click.argument('batch_file')
@click.argument('output_file')
@click.argument('item')
def inclusionproof(batch_file, output_file, item):
    """Save the inclusion proof for a specific item (file) to an output file."""
    filehandle = open(batch_file)
    batch_file_data = filehandle.read()
    filehandle.close()

    mt = tree.import_tree_from_json(batch_file_data)
    mt.build()

    inclusionproof = tree.get_inclusion_proof(mt, item)

    filehandle = open(output_file, 'w')
    filehandle.write(json.dumps(inclusionproof))
    filehandle.close()

    click.echo("Inclusion proof written to output file.")
