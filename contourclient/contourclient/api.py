"""API for Contour client."""

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
        A tuple where the first element is a boolean representing if the proof verifies, and the second element is the number of confirmations the proof's block has.
    """
