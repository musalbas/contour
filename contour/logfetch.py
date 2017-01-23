"""Log fetching operations."""
from contour.btcrpc import btcrpc, get_all_txs_by_address


def get_statement_roots_for_address(address):
    """
    Gets the statement merkle roots for a Bitcoin address.

    Args:
        The Bitcoin address.
    Returns:
        A list of hashes.
    """
    txs = get_all_txs_by_address(address)
    print(txs)
