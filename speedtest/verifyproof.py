"""Speed test for inclusion proof verification."""
import time
import statistics
import sys

import bson

from contour import auditor
from contour.btcnet import BlockchainManager

if __name__ == '__main__':
    proof_file = sys.argv[1]
    filehandle = open(proof_file, 'rb')
    proof_file_data = filehandle.read()
    filehandle.close()

    proof_file_dict = bson.loads(proof_file_data)
    proof = proof_file_dict['proof']
    digest_verifying = proof_file_dict['hash']

    blockchain = BlockchainManager().blockchain()

    time_lengths = []
    for i in range(1000000):
        print("Run %s" % (i+1))
        start_time = time.time()
        verification = auditor.verify_inclusion_proof(proof, digest_verifying, blockchain=blockchain)
        end_time = time.time()
        time_lengths.append(end_time - start_time)

    mean = sum(time_lengths) / len(time_lengths)
    sd = statistics.stdev(time_lengths)
    print("Average time: %ss" % mean)
    print("SD: %s" % sd)
