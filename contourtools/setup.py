from setuptools import setup


setup(
    name='contourtools',
    version='0.1',
    packages=['contourtools'],
    install_requires=[
        'click',
        'merkle',
        'pycoin',
        'appdirs',
        'configobj'
    ],
    entry_points='''
        [console_scripts]
        contourtools=contourtools.console:cli
    ''',
)
