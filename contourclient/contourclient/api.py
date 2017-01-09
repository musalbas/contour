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
