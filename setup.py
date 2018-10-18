"""
Setup file to manage package dependencies
"""

from setuptools import setup, find_packages

setup(
    name='py-uio',
    package_dir={'': 'src'},
    packages=find_packages(where='src') + ['ti', 'ti.icss'],
    py_modules=['devicetree', 'uio'],
    version_format='{tag}.dev{commits}+{sha}',
    setup_requires=['very-good-setuptools-git-version'],

    # metadata
    description="Userspace I/O in Python",
    author="Matthijs van Duin",
    url="https://github.com/mvdiuin/py-uio",
)
