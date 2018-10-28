#!/usr/bin/python3

from setuptools import setup, find_packages

setup(
    package_dir = { '': 'src' },
    packages = find_packages( where='src' ),
)
