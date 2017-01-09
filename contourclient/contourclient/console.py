"""Console application for Contour client."""

import logging
import sys

import click

from contourclient import api


def blockchain_index_change_callback(index):
    click.echo("Current block header: %s" % index)


class DevNull:
    def write(self, msg):
        pass


@click.group()
def cli():
    """Tools for Contour."""


@cli.command()
@click.argument('proof_file')
def verifyinclusionproof(proof_file):
    """Verify an inclusion proof."""
    pass


@cli.command()
def sync():
    """Sync the blockchain headers."""
    sys.stderr = DevNull()
    click.echo("Syncing blockchain. This may take a minute.")
    blockchain = api.sync(blockchain_index_change_callback)
    click.echo("Sync complete (no new blocks received in the past few seconds).")
