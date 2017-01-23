"""Speed test for building log entry."""
from binascii import unhexlify
import time
import sys

from contour.authority import LogEntry

if __name__ == '__main__':
    hashes_file = sys.argv[1]
    logentry = LogEntry()
    for line in open(hashes_file):
        logentry.add_sha256(unhexlify(line.rstrip()))

    time_lengths = []
    for i in range(20):
        print("Run %s" % (i+1))
        start_time = time.time()
        logentry.build()
        end_time = time.time()
        time_lengths.append(end_time - start_time)

    mean = sum(time_lengths) / len(time_lengths)
    print("Average time: %ss" % mean)
