"""API for Contour authorities."""
from hashlib import sha256

from pycoin.key import Key
from pycoin.serialize import h2b_rev

from contour.btcservices import get_tx_proof, send_op_return_tx, tx_for_id
from contour.merkle import MerkleTree


class LogEntry(object):
    """A log entry consists of a batch of one or more statements."""
    def __init__(self, statements=None, prehashed=False, tx_id=None):
        """
        Initialise log entry.

        statements: a list of statements in the entry.
        prehashed: True if the statements are SHA256 prehashed, otherwise False.
        tx_id: the Bitcoin transaction ID of the entry commitment if it has already been committed.
        """
        self.tree = MerkleTree()

        if statements:
            add_function = self.add_sha256 if prehashed else self.add
            [add_function(statement) for statement in statements]

        self.tx = tx_for_id(tx_id) if tx_id is not None else None
        self.tx_proof = None

    def add(self, data):
        """
        Add a statement to the entry.

        Args:
            data: the raw data of the statement.
        """
        digest = sha256(data).hexdigest()
        self.add_sha256(digest)

    def add_sha256(self, digest):
        """
        Add the SHA256 hash of a statement to the entry.

        Args:
            digest: the SHA256 hash of the statement.
        """
        self.tree.add_hash(digest)

    def attach_block(self):
        """Attempt to find the block that the committed transaction is mined in."""
        self.tx_proof = get_tx_proof(self.tx.id())

    def build(self):
        """Build the merkle tree for the entry."""
        self.tree.build()

    def commit(self, bitcoin_key_text, miner_fee=10000):
        """
        Commit the entry to the Bitcoin blockchain.

        Args:
            bitcoin_key_text: the Bitcoin private key for the new transaction, in WIF format.
            miner_fee: the miner fee to pay in Satoshis (default: 10000 Satoshis).
        Returns:
            The transaction ID.
        """
        bitcoin_key = Key.from_text(bitcoin_key_text)
        self.tx = send_op_return_tx(bitcoin_key, self.tree.root.val, miner_fee)

        return self.tx.id()

    def get_inclusion_proof(self, index):
        """
        Get the inclusion proof in the Bitcoin blockchain for a statement in the log entry.

        Args:
            index: the index number of the statement.
        Returns:
            The inclusion proof.
        """
        return self.tx_proof + (self.tx.as_bin(), self.tree.get_inclusion_proof(index))
