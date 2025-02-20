# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('LICENSE') as f:
    license = f.read()

setup(
    name='cfgr',
    version='0.1.0',
    description='Config file manage and diff',
    author='Eric Gustafson',
    author_email='ericg@elfwerks.io',
    url='https://github.com/egustafson/cfgr',
    license=license,
    packages=find_packages(exclude=('tests','docs')),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'cfgr = cfgr:cli',
        ]
    }
)
