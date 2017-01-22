"""Bitcoin operations that rely on external services."""
from binascii import hexlify, unhexlify
import io

from pycoin.block import Block
from pycoin.key import Key
from pycoin.serialize import b2h_rev
from pycoin.services.blockchain_info import spendables_for_address
from pycoin.tx import Tx, script
from pycoin.tx.tx_utils import sign_tx
from pycoin.tx.TxOut import TxOut, standard_tx_out_script
import requests

from contour.localdata import config, get_block, put_block
from contour.merkle import MerkleTree
from contour.utils import DoubleSHA256


def broadcast_tx(tx):
    """
    Broadcast a Bitcoin transaction.

    Args:
        tx: a Tx object.
    """
    requests.post('https://api.blockcypher.com/v1/btc/main/txs/push', json={'tx': tx.as_hex()})


def tx_for_id(tx_id):
    """
    Get a transaction by ID.

    Args:
        tx_id: the transaction ID.
    Returns:
        The Tx object.
    """
    result = requests.get('https://api.blockcypher.com/v1/btc/main/txs/%s?token=&includeHex=true' % tx_id).json()
    tx = Tx.parse(io.BytesIO(unhexlify(result.get("hex"))))
    return tx


def block_by_hash(digest):
    """
    Get a block by hash.

    Args:
        digest: the hash of the block.
    Returns:
        A Block object.
    """
    raw_block = get_block(digest)
    if raw_block is None:
        raw_block = requests.get('https://blockchain.info/rawblock/%s?format=hex' % digest).text
        raw_block = unhexlify(raw_block)
        put_block(digest, raw_block)

    block = Block.parse(io.BytesIO(raw_block))
    return block


def block_hash_for_tx_id(tx_id):
    """
    Get the block hash for a transaction.

    Args:
        tx_id: the Bitcoin transaction ID.
    Returns:
        The block hash.
    """
    if tx_id is not in config['block_hash_for_tx_id']:
        result = requests.get('https://api.blockcypher.com/v1/btc/main/txs/%s?token=' % tx_id).json()
        if result['block_hash']:
            config['block_hash_for_tx_id'][tx_id] = result['block_hash']
            return result['block_hash']
        else:
            return None
    else:
        return config['block_hash_for_tx_id']


def get_tx_proof(tx_id):
    """
    Get the data needed to prove that a transaction is included in a block.

    Args:
        tx: the Bitcoin transaction ID.
    Returns:
        A tuple containing (blockheader, transaction_merkle_proof).
    """
    block_hash = block_hash_for_tx_id(tx_id)
    if block_hash is None:
        raise Exception("this transaction is unconfirmed")

    block = block_by_hash(block_hash)

    tx_hashes = []
    for i in range(len(block.txs)):
        block_tx = block.txs[i]
        if block_tx.id() == tx_id:
            tx_index = i
        tx_hashes.append(block_tx.hash())

    mt = MerkleTree(tx_hashes, prehashed=True, hash_function=DoubleSHA256)
    mt.build(bitcoin=True)

    blockheader_raw = io.BytesIO()
    block.as_blockheader().stream(blockheader_raw)
    blockheader_raw = blockheader_raw.getvalue()

    return (blockheader_raw, mt.get_inclusion_proof(tx_index))


def send_op_return_tx(key, message, fee=10000):
    """
    Send an transaction with an OP_RETURN output.

    Args:
        key: the Bitcoin Key to send the transaction from.
        message: the message to include in OP_RETURN.
        fee: the miner fee that should be paid in Satoshis.
    Returns:
        The broadcasted Tx.
    """
    address = key.address()

    if len(message) > 80:
        raise ValueError("message must not be longer than 80 bytes")
    message = hexlify(message).decode()

    spendables = spendables_for_address(address)
    bitcoin_sum = sum(spendable.coin_value for spendable in spendables)
    if bitcoin_sum < fee:
        raise Exception("not enough bitcoin to cover fee")

    inputs = [spendable.tx_in() for spendable in spendables]

    outputs = []
    if bitcoin_sum > fee:
        change_output_script = standard_tx_out_script(address)
        outputs.append(TxOut(bitcoin_sum - fee, change_output_script))

    op_return_output_script = script.tools.compile('OP_RETURN %s' % message)
    outputs.append(TxOut(0, op_return_output_script))

    tx = Tx(version=1, txs_in=inputs, txs_out=outputs)
    tx.set_unspents(spendables)
    sign_tx(tx, wifs=[key.wif()])

    broadcast_tx(tx)

    return tx
