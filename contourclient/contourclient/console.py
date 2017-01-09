"""Console application for Contour client."""

import logging
import json
import sys

import click

from contourclient import api


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
def verifyinclusionproof(proof_file):
    """Verify an inclusion proof."""
    filehandle = open(proof_file)
    proof_file_data = filehandle.read()
    filehandle.close()

    proof = json.loads(proof_file_data)
    verification = api.verify_inclusion_proof(proof)
    click.echo(verification)


@cli.command()
def sync():
    """Sync the blockchain headers."""
    sys.stderr = DevNull() # Suppress verbose errors and exceptions

    click.echo("Syncing blockchain. This may take a minute or two.")
    blockchain = api.sync(length_change_callback=blockchain_length_change_callback)
    click.echo("Sync complete (no new blocks received in the past few seconds).")
