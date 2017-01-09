"""Merkle tree operations."""

import json
import os

from pycoin.tx import Tx
from merkle import MerkleTree

from contourtools import btc


def build_tree_from_directory(source_directory):
    """
    Build a merkle tree using the data from files in a directory as leaves.

    Args:
        source_directory: the source directory.
    Returns:
        The MerkleTree.
    """
    mt = MerkleTree()
    filenames = next(os.walk(source_directory))[2]

    for filename in filenames:
        filehandle = open(os.path.join(source_directory, filename))
        filedata = filehandle.read()
        filehandle.close()

        mt.add(filedata)

    mt.build()
    mt.keys = filenames

    return mt


def export_tree_as_json(mt):
    """
    Export a tree in JSON format.

    Args:
        mt: the MerkleTree.

    Returns:
        A JSON string.
    """
    if not hasattr(mt, 'keys'):
        mt.keys = []
    if not hasattr(mt, 'txdata'):
        mt.txdata = ''
    if not hasattr(mt, 'blockpath'):
        mt.blockpath = ()

    return json.dumps((mt.keys, mt.get_all_hex_chains(), mt.txdata, mt.blockpath))


def import_tree_from_json(json_string):
    """
    Import a tree from a JSON string.

    Args:
        json_string: the JSON string.

    Returns:
        The MerkleTree.
    """
    mt_json = json.loads(json_string)

    mt = MerkleTree()
    mt.keys = mt_json[0]
    mt.txdata = mt_json[2]
    mt.blockpath = mt_json[3]

    for item in mt_json[1]:
        mt.add_hash(item[0][0])

    return mt


def btc_commit_tree(mt, btc_key):
    """
    Commit a merkle tree to the Bitcoin blockchain.

    Args:
        mt: the MerkleTree.
        btc_key: the Bitcoin key.
    Returns:
        The Bitcoin Tx.
    """
    root = mt.get_chain(0)[-1][0]

    tx = btc.send_op_return_tx(btc_key, root)

    mt.txdata = tx.as_hex()

    return tx


def btc_attach_block(mt):
    """
    Attach attach block and merkle path details to a committed merkle tree.

    Args:
        mt: the MerkleTree.
    """
    tx = Tx.from_hex(mt.txdata)
    mt.blockpath = btc.get_block_path_for_tx(tx)


def get_inclusion_proof(mt, item_key):
    """
    Get the inclusion proof for a specific item in the tree.

    Args:
        mt: the MerkleTree.
        item_key: the key name of the item.
    Returns:
        A tuple containing (txdata, blockpath, item_merkle_proof).
    """
    item_index = mt.keys.index(item_key)
    inclusionproof = (mt.txdata, mt.blockpath, mt.get_hex_chain(item_index))
    return inclusionproof
