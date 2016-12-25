"""Setup for Contour client."""

from setuptools import setup


setup(
    name='contourclient',
    version='0.1',
    packages=['contourclient'],
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        contourclient=contourclient.console:cli
    ''',
)
