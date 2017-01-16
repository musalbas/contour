"""Console utilities for Contour authority operators."""
from binascii import unhexlify
import bson

import click

from contour.authority import LogEntry


@click.group()
def cli():
    """Utilities for Contour authority operators."""


@cli.command()
@click.argument('hashes_file')
@click.argument('bitcoin_key')
def commit(hashes_file, bitcoin_key):
    """Commit a log entry to the Bitcoin blockchain."""
    logentry = LogEntry()

    for line in open(hashes_file):
        logentry.add_sha256(unhexlify(line.rstrip()))
    logentry.build()

    tx_id = logentry.commit(bitcoin_key)

    click.echo("Log entry committed as transaction with ID: %s" % tx_id)


@cli.command()
@click.argument('hashes_file')
@click.argument('statement_index', type=int)
@click.argument('tx_id')
def proof(hashes_file, statement_index, tx_id):
    """Get the inclusion proof for a statement."""
    logentry = LogEntry(tx_id=tx_id)

    index = 0
    for line in open(hashes_file):
        digest = unhexlify(line.rstrip())
        logentry.add_sha256(digest)
        if index == statement_index:
            proving_digest = digest
        index += 1
    logentry.build()

    logentry.attach_block()
    proof = logentry.get_inclusion_proof(statement_index)

    click.echo(bson.dumps({'proof': proof, 'hash': proving_digest}))
