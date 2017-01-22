"""API for Contour auditor."""
from binascii import hexlify
import io

from pycoin.block import BlockHeader
from pycoin.tx import Tx

from contour.btcnet import BlockchainManager
from contour.merkle import check_inclusion_proof, MerkleError
from contour.utils import DoubleSHA256


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


def verify_inclusion_proof(proof, digest_verifying):
    """
    Verifies an inclusion proof.

    Args:
        proof: the proof information tuple.
        digest_verifying: the hash of the statement that is being verified as included.
    Returns:
        A tuple where the first element is a boolean representing if the proof verifies, the second element is the number of confirmations the proof's block has and the third element is the Bitcoin address of the transaction.
    """
    # Parse transaction
    tx = Tx.parse(io.BytesIO(proof[2]))
    address = tx.txs_in[0].bitcoin_address()

    # Check that the block is in the blockchain, and get confirmations
    blockheader = BlockHeader.parse(io.BytesIO(proof[0]))
    bm = BlockchainManager()
    blockchain = bm.blockchain()
    block_index = blockchain.index_for_hash(blockheader.hash())
    if not block_index:
        # Block not found in blockchain; fail verification
        return (False, 0, address)
    latest_block_index = blockchain.index_for_hash(blockchain.last_block_hash())
    confirmations = latest_block_index - block_index

    # Check the merkle path to the transaction is valid
    try:
        check_inclusion_proof(proof[1], blockheader.merkle_root, tx.hash(), hash_function=DoubleSHA256)
    except MerkleError:
        return (False, confirmations, address)

    # Check merkle path to item whose hash is being verified is valid
    op_return_data = tx.tx_outs_as_spendable()[1].script[-32:] # TODO improve this hack (conditions for verification are too strict)
    try:
        check_inclusion_proof(proof[3], op_return_data, digest_verifying)
    except MerkleError:
        return (False, confirmations, address)

    return (True, confirmations, address)
