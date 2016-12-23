from binascii import hexlify

from pycoin.key import Key
from pycoin.tx import script, Tx
from pycoin.tx.tx_utils import sign_tx
from pycoin.tx.TxOut import TxOut
from pycoin.ui import standard_tx_out_script
from pycoin.services.blockchain_info import BlockchainInfoProvider
from pycoin.services.blockcypher import BlockcypherProvider
from pycoin.encoding import double_sha256
import merkle
from merkle import MerkleTree

from localconfig import config


class DoubleSHA256(object):
    def __init__(self, data):
        self.data = data

    def digest(self):
        return double_sha256(self.data)


def _broadcast_tx(tx):
    provider = BlockcypherProvider(netcode='BTC')
    return provider.broadcast_tx(tx)


def _spendables_for_address(address):
    provider = BlockchainInfoProvider(netcode='BTC')
    return provider.spendables_for_address(address)


def _block(hash):
    provider = BlockchainInfoProvider(netcode='BTC')
    return provider.block(hash)


def _block_hash_for_tx(tx):
    provider = BlockcypherProvider(netcode='BTC')
    return provider.block_hash_for_tx(tx)


def get_block_path_for_tx(tx):
    block_hash = _block_hash_for_tx(tx)
    if block_hash is None:
        raise Exception("this transaction is unconfirmed")
    block = _block(block_hash)

    txhashes = []
    for i in range(len(block.txs)):
        blocktx = block.txs[i]
        if blocktx.id() == tx.id():
            txindex = i
        txhashes.append(blocktx.hash().encode('hex'))

    merkle.hash_function = DoubleSHA256
    mt = MerkleTree(txhashes, True)
    mt.build(bitcoin=True)
    return (block.as_blockheader().hash().encode('hex'), mt.get_hex_chain(txindex))


def send_op_return_tx(key, message, fee=10000):
    address = key.address()

    if len(message) > 80:
        raise ValueError("message must not be longer than 80 bytes")
    message = hexlify(message).decode('utf8')

    spendables = _spendables_for_address(address)
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

    _broadcast_tx(tx)

    return tx


def import_key(key_text):
    key = Key.from_text(key_text)
    address = key.address()

    if address in config['btckeys']:
        raise Exception("key already imported")

    config['btckeys'][address] = key.as_text()
    config.write()

    return address


def get_key(address):
    return Key.from_text(config['btckeys'][address])


def keys():
    return config['btckeys'].copy()
