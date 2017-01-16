"""Console utilities for Contour auditor."""
from binascii import hexlify
import bson
import logging
import sys

import click

from contour import auditor


class DevNull:
    """File stream class for writing to nothing."""
    def write(self, msg):
        """
        Write to nothing.

        Args:
            msg: the message to write.
        """
        pass


def blockchain_length_change_callback(length):
    """
    Callback handler for blockchain length change during sync.

    Args:
        length: the length of the blockchain.
    """
    click.echo("Current blockchain length: %s" % length)


@click.group()
def cli():
    """Tools for Contour."""


@cli.command()
@click.argument('proof_file')
def verify(proof_file):
    """Verify an inclusion proof."""
    filehandle = open(proof_file, 'rb')
    proof_file_data = filehandle.read()
    filehandle.close()

    proof_file_dict = bson.loads(proof_file_data)
    proof = proof_file_dict['proof']
    digest_verifying = proof_file_dict['hash']
    verification = auditor.verify_inclusion_proof(proof, digest_verifying)

    if verification[0]:
        click.echo("Verification successful.")
        click.echo("Item hash: %s" % hexlify(digest_verifying).decode())
        click.echo("Number of confirmations: %s" % verification[1])
    else:
        click.echo("Verification failed.")


@cli.command()
def sync():
    """Sync the blockchain headers."""
    sys.stderr = DevNull() # Suppress verbose errors and exceptions

    click.echo("Syncing blockchain. This may take a minute or two.")
    blockchain = auditor.sync(length_change_callback=blockchain_length_change_callback)
    click.echo("Sync complete (no new blocks received in the past few seconds).")
