import click

import tree


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
