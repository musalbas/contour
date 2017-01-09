"""Bitcoin operations."""

from binascii import hexlify

from pycoin.key import Key
from pycoin.tx import script, Tx
from pycoin.tx.tx_utils import sign_tx
from pycoin.tx.TxOut import TxOut
from pycoin.ui import standard_tx_out_script
from pycoin.services.blockchain_info import BlockchainInfoProvider
from pycoin.services.blockcypher import BlockcypherProvider
from pycoin.encoding import double_sha256
from merkle import MerkleTree, hash_function

from contourtools.localconfig import config


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


def broadcast_tx(tx):
    """
    Broadcast a Bitcoin transaction.

    Args:
        tx: a Tx object.
    Returns:
        A dict of details about the transaction.
    """
    provider = BlockcypherProvider(netcode='BTC')
    return provider.broadcast_tx(tx)


def spendables_for_address(address):
    """
    Get the spendable outputs for an address.

    Args:
        address: the Bitcoin address.
    Returns:
        A list of Spendable objects.
    """
    provider = BlockchainInfoProvider(netcode='BTC')
    return provider.spendables_for_address(address)


def block(hash):
    """
    Get a block by hash.

    Args:
        hash: the hash of the block.
    Returns:
        A Block object.
    """
    provider = BlockchainInfoProvider(netcode='BTC')
    return provider.block(hash)


def block_hash_for_tx(tx):
    """
    Get the block hash for a transaction.

    Args:
        tx: the Tx object.
    Returns:
        The block hash.
    """
    provider = BlockcypherProvider(netcode='BTC')
    return provider.block_hash_for_tx(tx)


def get_block_path_for_tx(tx):
    """
    Get the data needed to prove that a transaction is included in a block.

    Args:
        tx: the Bitcoin transaction.
    Returns:
        A tuple containing (blockheader, transaction_merkle_proof).
    """
    block_hash = block_hash_for_tx(tx)
    if block_hash is None:
        raise Exception("this transaction is unconfirmed")

    block = block(block_hash)

    txhashes = []
    for i in range(len(block.txs)):
        blocktx = block.txs[i]
        if blocktx.id() == tx.id():
            txindex = i
        txhashes.append(blocktx.hash().encode('hex'))

    hash_function = DoubleSHA256
    mt = MerkleTree(txhashes, prehashed=True)
    mt.build(bitcoin=True)

    return (block.as_blockheader().get_hex(), mt.get_hex_chain(txindex))


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
    message = hexlify(message).decode('utf8')

    spendables = spendables_for_address(address)
    btc_sum = sum(spendable.coin_value for spendable in spendables)
    if btc_sum < fee:
        raise Exception("not enough bitcoin to cover fee")

    inputs = [spendable.tx_in() for spendable in spendables]

    outputs = []
    if btc_sum > fee:
        change_output_script = standard_tx_out_script(address)
        outputs.append(TxOut(btc_sum - fee, change_output_script))

    op_return_output_script = script.tools.compile("OP_RETURN %s" % message)
    outputs.append(TxOut(0, op_return_output_script))

    tx = Tx(version=1, txs_in=inputs, txs_out=outputs)
    tx.set_unspents(spendables)
    sign_tx(tx, wifs=[key.wif()])

    broadcast_tx(tx)

    return tx


def import_key(key_text):
    """
    Import a Bitcoin key to the local config.

    Args:
        key_text: a WIF-encoded Bitcoin private key.
    Returns:
        The Key object.
    """
    key = Key.from_text(key_text)
    address = key.address()

    if address in config['btckeys']:
        raise Exception("key already imported")

    config['btckeys'][address] = key.as_text()
    config.write()

    return key


def get_key(address):
    """
    Get an imported key.

    Args:
        The Bitcoin address of the key.
    Returns:
        The Key object.
    """
    return Key.from_text(config['btckeys'][address])


def keys():
    """Returns a list of imported keys."""
    return config['btckeys'].copy()
