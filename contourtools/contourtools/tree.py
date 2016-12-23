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
    if not hasattr(mt, 'keys'):
        mt.keys = []
    if not hasattr(mt, 'txdata'):
        mt.txdata = ''
    if not hasattr(mt, 'blockpath'):
        mt.blockpath = ()
    return json.dumps((mt.keys, mt.get_all_hex_chains(), mt.txdata, mt.blockpath))


def import_tree_from_json(json_string):
    mt_json = json.loads(json_string)
    mt = MerkleTree()
    mt.keys = mt_json[0]
    mt.txdata = mt_json[2]
    mt.blockpath = mt_json[3]

    for item in mt_json[1]:
        mt.add_hash(item[0][0])

    return mt
