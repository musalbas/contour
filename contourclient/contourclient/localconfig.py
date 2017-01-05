"""Local configuration file management."""

import os

from appdirs import user_config_dir
from configobj import ConfigObj

# Create configuration directory in case it does not exist.
try:
    os.makedirs(user_config_dir('contourclient'))
except OSError:
    if not os.path.isdir(user_config_dir('contourclient')):
        raise

# Determine cross-platform configuration file path.
configfile = os.path.join(user_config_dir('contourclient'), 'config')

# Create configuration object.
config = ConfigObj(configfile)

bcvfile = os.path.join(user_config_dir('contourclient'), 'bcv')
bcvconfig = ConfigObj(bcvfile)

if 'node_tuples' not in bcvconfig:
    bcvconfig['node_tuples'] = []
