"""Speed test for generating an OP_RETURN transaction."""
from binascii import hexlify, unhexlify
import time
import statistics
import sys

from pycoin.key import Key
from pycoin.tx import Tx, script
from pycoin.tx.tx_utils import sign_tx
from pycoin.tx.TxOut import TxOut, standard_tx_out_script

from contour.btcservices import spendables_for_address


def dummy_op_return_tx(key, message, spendables, fee=10000):
    address = key.address()

    if len(message) > 80:
        raise ValueError("message must not be longer than 80 bytes")
    message = hexlify(message).decode()

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

    return tx

if __name__ == '__main__':
    key = Key.from_text(sys.argv[1])

    spendables = spendables_for_address(key.address())

    time_lengths = []
    for i in range(1000):
        print("Run %s" % (i+1))
        start_time = time.time()
        dummy_op_return_tx(key, unhexlify('ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'), spendables)
        end_time = time.time()
        time_lengths.append(end_time - start_time)

    mean = sum(time_lengths) / len(time_lengths)
    sd = statistics.stdev(time_lengths)
    print("Average time: %ss" % mean)
    print("SD: %s" % sd)
