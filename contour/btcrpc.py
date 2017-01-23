"""Bitcoin Core RPC interface."""
from bitcoinrpc.authproxy import AuthServiceProxy

from contour.localdata import config

btcrpc = AuthServiceProxy(config['btc_rpc_uri'])


def get_all_txs_by_address(address):
    """
    Get all the transactions for an address.

    Args:
        address: the Bitcoin address.
    Returns:
        A list of transaction dicts.
    """
    all_txs = []
    current_txs = None
    skip = 0
    while current_txs != []:
        current_txs = btcrpc.listtransactions('', 1000, skip, True)
        skip += 1000
        filtered_txs = filter(lambda tx: tx['address'] == address, current_txs)
        all_txs += filtered_txs

    return all_txs
