"""Bitcoin network operations."""

import asyncio
import threading
import time

from appdirs import user_config_dir
from pycoin.blockchain.BlockChain import BlockChain
from pycoinnet.util.BlockChainStore import BlockChainStore
from pycoinnet.helpers.dnsbootstrap import dns_bootstrap_host_port_q
from pycoinnet.helpers.networks import MAINNET

from contourclient.btcclient import Client


def should_download_block_false(block_hash, block_index):
    """
    Callback function for Client to indicate that a full block should never be downloaded.

    Args:
        block_hash: the hash of the block.
        block_index: the index of the block.
    Returns:
        Always returns False.
    """
    return False


class BlockchainManager(object):
    """Client to synchronise blockchain headers."""
    def __init__(self):
        """Initialise the blockchain manager."""
        self.bcs = BlockChainStore(user_config_dir('contourclient'))
        self.client = None

    def _blockchain_change_callback(self, blockchain, ops):
        pass

    def _sync_loop(self, timeout, length_change_callback):
        interval_time = 1
        current_length = 0
        time_elapsed_since_length_change = 0
        while True:
            new_length = self.blockchain().length()
            if current_length == new_length:
                time_elapsed_since_length_change += interval_time
                if time_elapsed_since_length_change > timeout:
                    self.event_loop.stop()
                    break
            else:
                time_elapsed_since_length_change = 0
                current_length = new_length
                if length_change_callback:
                    length_change_callback(current_length)

            time.sleep(interval_time)

    def sync(self, timeout, length_change_callback=None):
        """
        Synchronise the blockchain to the latest headers.

        Args:
            timeout: the timeout to stop after not receiving any new blocks.
            length_change_callback: a function to call with arg (length) when the blockchain length changes.
        """
        self.client = Client(
            network=MAINNET,
            host_port_q=dns_bootstrap_host_port_q(MAINNET),
            should_download_block_f=should_download_block_false,
            block_chain_store=self.bcs,
            blockchain_change_callback=self._blockchain_change_callback,
        )

        self.event_loop = asyncio.get_event_loop()
        t = threading.Thread(target=self._sync_loop, args=(timeout, length_change_callback))
        t.start()
        self.event_loop.run_forever()

    def blockchain(self):
        """Returns the current Blockchain object."""
        if self.client:
            return self.client.blockhandler.block_chain
        else:
            blockchain = BlockChain(did_lock_to_index_f=self.bcs.did_lock_to_index)
            blockchain.preload_locked_blocks(self.bcs.headers())
            return blockchain
