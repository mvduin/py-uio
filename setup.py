#!/usr/bin/python3

from setuptools import setup, find_namespace_packages

setup(
    package_dir = { '': 'src' },
    packages = find_namespace_packages( where='src' ),
)
