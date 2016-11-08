import json
import os

from merkle import MerkleTree


def build_tree_from_directory(source_directory):
    mt = MerkleTree()
    filenames = next(os.walk(source_directory))[2]

    for filename in filenames:
        filehandle = open(os.path.join(source_directory, filename))
        filedata = filehandle.read()
        filehandle.close()

        mt.add(filedata)

    mt.build()
    mt.keys = filenames

    return mt


def export_tree_as_json(mt):
    return json.dumps((mt.keys, mt.get_all_hex_chains()))
