"""API for Contour client."""

from merkle import check_hex_chain
from pycoin.block import BlockHeader

from contourclient.btcnet import BlockchainManager


def sync(timeout=5, length_change_callback=None):
    """
    Sync to the latest blockchain headers.

    Args:
        timeout: the timeout to stop after not receiving any new blocks.
        length_change_callback: a function to call with arg (length) when the blockchain length changes.
    Returns:
        Blockchain object.
    """
    bm = BlockchainManager()
    bm.sync(timeout, length_change_callback)

    return bm.blockchain()


def verify_inclusion_proof(proof):
    """
    Verifies an inclusion proof.

    Args:
        proof: the proof information tuple.
    Returns:
        A tuple where the first element is a boolean representing if the proof verifies, the second element is the number of confirmations the proof's block has, and the third element is the hash being proved.
    """
    # Check that the block is in the blockchain
    blockheader = BlockHeader.from_bin(bytes.fromhex(proof[1][0]))
    print(blockheader)
