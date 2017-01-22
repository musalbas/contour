"""Bitcoin Core RPC interface."""
from bitcoinrpc.authproxy import AuthServiceProxy

from contour.localdata import config

btcrpc = AuthServiceProxy(config['btc_rpc_uri'])
