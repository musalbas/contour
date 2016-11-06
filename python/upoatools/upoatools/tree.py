import os

from merkle import MerkleTree


def build_tree_from_directory(source_directory):
    mt = MerkleTree()

    filepaths = [os.path.join(source_directory, filename) for filename in next(os.walk(source_directory))[2]]
    for filepath in filepaths:
        filehandle = open(filepath)
        filedata = filehandle.read()
        filehandle.close()

        mt.add(filedata)

    print mt.build()
