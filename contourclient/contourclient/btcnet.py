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
    sync_timeout = 3

    def __init__(self):
        """Initialise the blockchain manager."""
        self.bcs = BlockChainStore(user_config_dir('contourclient'))
        self.client = None

    def _blockchain_change_callback(self, blockchain, ops):
        pass

    def _sync_loop(self, index_change_callback):
        index = 0
        time_elapsed_since_index = 0
        while True:
            new_index = self.blockchain().index_for_hash(self.blockchain().last_block_hash())
            if new_index != index:
                time_elapsed_since_index = 0
                index = new_index
                if index_change_callback and new_index is not None:
                    index_change_callback(index)
            else:
                time_elapsed_since_index += 1
            if time_elapsed_since_index > self.sync_timeout:
                self.event_loop.stop()
                self.event_loop.close()
                break
            time.sleep(1)

    def sync(self, index_change_callback=None):
        """
        Synchronise the blockchain to the latest headers.

        Args:
            index_change_callback: a function to call with args (index) when the latest blockchain index changes.
        """
        self.client = Client(
            network=MAINNET,
            host_port_q=dns_bootstrap_host_port_q(MAINNET),
            should_download_block_f=should_download_block_false,
            block_chain_store=self.bcs,
            blockchain_change_callback=self._blockchain_change_callback,
        )

        self.event_loop = asyncio.get_event_loop()
        t = threading.Thread(target=self._sync_loop, args=(index_change_callback,))
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
