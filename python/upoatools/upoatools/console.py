import click

import tree


@click.group()
def cli():
    """Tools for Untrusted Proofs of Auditability."""

@cli.command()
@click.argument('source_directory')
def buildtree(source_directory):
    """Build a merkle tree of items for auditing."""
    return tree.build_tree_from_directory(source_directory)
