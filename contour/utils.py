"""Utility code."""
from pycoin.encoding import double_sha256


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
