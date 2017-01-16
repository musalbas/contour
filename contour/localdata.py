"""Local data management."""
import os

from appdirs import user_config_dir

data_dir = user_config_dir('contour')
blocks_dir = os.path.join(data_dir, 'blocks_cache')

try:
    os.makedirs(data_dir)
except OSError:
    if not os.path.isdir(data_dir):
        raise

try:
    os.makedirs(blocks_dir)
except OSError:
    if not os.path.isdir(blocks_dir):
        raise


def put_block(digest, raw_block):
    """
    Write a block to the block cache.

    Args:
        digest: the hash of the block.
        raw_block: the data of the block.
    """
    filehandle = open(os.path.join(blocks_dir, digest), 'wb')
    filehandle.write(raw_block)
    filehandle.close()


def get_block(digest):
    """
    Get a block from the block cache.

    Args:
        digest: the hash of the block.
    Returns:
        The data of the block if it exists, otherwise None.
    """
    try:
        filehandle = open(os.path.join(blocks_dir, digest), 'rb')
    except OSError:
        return None

    raw_block = filehandle.read()
    filehandle.close()

    return raw_block
