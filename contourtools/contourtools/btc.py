from binascii import hexlify

from pycoin.key import Key
from pycoin.tx import script, Tx
from pycoin.tx.tx_utils import sign_tx
from pycoin.tx.TxOut import TxOut
from pycoin.ui import standard_tx_out_script
from pycoin.services.blockchain_info import BlockchainInfoProvider
from pycoin.services.blockcypher import BlockcypherProvider

from localconfig import config


def _broadcast_tx(tx):
    provider = BlockcypherProvider('BTC')
    return provider.broadcast_tx(tx)


def _spendables_for_address(address):
    provider = BlockchainInfoProvider('BTC')
    return provider.spendables_for_address(address)


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
