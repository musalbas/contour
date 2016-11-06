from setuptools import setup

setup(
    name='upoatools',
    version='0.1',
    packages=['upoatools'],
    install_requires=[
        'click',
    ],
    entry_points='''
        [console_scripts]
        upoatools=upoatools.console:cli
    ''',
)
