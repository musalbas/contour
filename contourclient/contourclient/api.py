"""API for Contour client."""

from binascii import hexlify

from merkle import check_hex_chain
from pycoin.block import BlockHeader

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

    return (True, confirmations, hash_proving)
