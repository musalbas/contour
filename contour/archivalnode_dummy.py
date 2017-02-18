"""Dummy Contour archival node."""
from flask import Flask

from contour.btcnet import BlockchainManager


class ArchivalNode():
    """Contour archival node."""
    def __init__(self, authority_bitcoin_address, authority_data_url):
        """
        Initialise archival node.

        Args:
            authority_bitcoin_address: the Bitcoin address of the authority.
            authority_data_url: the URL of the authority's data archives.
        """
        app = Flask(__name__)

        @app.route('/get_arch_state')
        def get_arch_state():
            return BlockchainManager().blockchain().last_block_hash()

        app.run()
