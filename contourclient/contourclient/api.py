"""API for Contour client."""

from binascii import hexlify
from hashlib import sha256

from merkle import check_hex_chain, MerkleError
import merkle
from pycoin.block import BlockHeader
from pycoin.encoding import double_sha256
from pycoin.tx import Tx

from contourclient.btcnet import BlockchainManager


class DoubleSHA256(object):
    """Class to double SHA256 hash data."""
    def __init__(self, data):
        """
        Initialise hash.

        Args:
            data: the data to hash.
        """
        self.data = data

    def digest(self):
        """Returns the digest of the data."""
        return double_sha256(self.data)


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
    # Get hash being proved for inclusion
    hash_proving = proof[2][0][0]

    # Check that the block is in the blockchain, and get confirmations
    blockheader = BlockHeader.from_bin(bytes.fromhex(proof[1][0]))
    bm = BlockchainManager()
    blockchain = bm.blockchain()
    block_index = blockchain.index_for_hash(blockheader.hash())
    if not block_index:
        # Block not found in blockchain; fail verification
        return (False, 0, hash_proving)
    latest_block_index = blockchain.index_for_hash(blockchain.last_block_hash())
    confirmations = latest_block_index - block_index

    # Check that merkle root in the block merkle path matches the block
    if hexlify(blockheader.merkle_root).decode() != proof[1][1][-1][0]:
        return (False, confirmations, hash_proving)

    # Check the merkle path to the transaction is valid
    merkle.hash_function = DoubleSHA256
    try:
        check_hex_chain(proof[1][1])
    except MerkleError:
        return (False, confirmations, hash_proving)

    # Check merkle root in merkle path to item matches transaction OP_RETURN hash
    tx = Tx.from_hex(proof[0])
    op_return_data = hexlify(tx.tx_outs_as_spendable()[1].script).decode()[4:] # TODO improve this hack (conditions for verification are too strict)
    if op_return_data != proof[2][-1][0]:
        return (False, confirmations, hash_proving)

    # Check merkle path to item whose hash is being verified is valid
    merkle.hash_function = sha256
    try:
        check_hex_chain(proof[2])
    except MerkleError:
        return (False, confirmations, hash_proving)

    return (True, confirmations, hash_proving)
