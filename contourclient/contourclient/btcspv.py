"""Bitcoin SPV network operations."""

from appdirs import user_config_dir
from pycoinnet.examples.spvclient import SPVClient
from pycoinnet.helpers.networks import MAINNET
from pycoinnet.util.BlockChainView import BlockChainView

from localconfig import bcvconfig


class ContourSPV(object):
    """Bitcoin SPV client for Contour operations."""

    def __init__(self):
        """Initialise SPV client."""
        self.spv = SPVClient(MAINNET)
