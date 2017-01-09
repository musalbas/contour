"""API for Contour client."""

from contourclient.btcnet import BlockchainManager


def sync(index_change_callback=None):
    """
    Sync to the latest blockchain headers.

    Args:
        index_change_callback: a function to call with args (index) when the latest blockchain index changes.
    Returns:
        Blockchain object.
    """
    bm = BlockchainManager()
    bm.sync(index_change_callback)

    return bm.blockchain()
