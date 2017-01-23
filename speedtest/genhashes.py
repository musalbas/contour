"""Generate hashes for input file (not a speed test)."""
import random
from hashlib import sha256
import sys

if __name__ == '__main__':
    for i in range(int(sys.argv[1])):
        print(sha256(str(random.random()).encode('utf-8')).hexdigest())
