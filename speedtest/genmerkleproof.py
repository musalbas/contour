"""Speed test for building merkle proofs."""
from binascii import unhexlify
import time
import sys

from contour.merkle import MerkleTree

if __name__ == '__main__':
    num_items = int(sys.argv[1])

    mt = MerkleTree()
    for i in range(num_items):
        mt.add_hash(unhexlify('ca978112ca1bbdcafac231b39a23dc4da786eff8147c4e72b9807785afee48bb'))
        if i % 10000 == 0:
            print("Adding hash %s" % i)

    print("Building tree...")
    mt.build()

    time_lengths = []
    for i in range(1000000):
        print("Run %s" % (i+1))
        start_time = time.time()
        mt.get_inclusion_proof(0)
        end_time = time.time()
        time_lengths.append(end_time - start_time)

    mean = sum(time_lengths) / len(time_lengths)
    print("Average time: %ss" % mean)
