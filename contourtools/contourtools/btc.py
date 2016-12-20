from pycoin.key import Key

from localconfig import config


def import_key(key_text):
    key = Key.from_text(key_text)
    address = key.address()

    if address in config['btckeys']:
        raise Exception("key already imported")

    config['btckeys'][address] = key.as_text()
    config.write()

    return address


def keys():
    return config['btckeys'].copy()
