import unittest

from merkle import MerkleTree

from contourtools.tree import *


class TestTree(unittest.TestCase):
    def setUp(self):
        mt = MerkleTree()
        mt.add('a')
        mt.add('b')
        mt.build()

        self.mt = mt

    def test_json(self):
        imported_mt = import_tree_from_json(export_tree_as_json(self.mt))
        imported_mt.build()
        self.assertEqual(self.mt.get_all_chains(), imported_mt.get_all_chains())

if __name__ == '__main__':
    unittest.main()
