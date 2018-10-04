#!/usr/bin/env python3

from setuptools import setup, find_packages

print("Installing pyuio")

setup(name='pyuio',
      version='0.1',
      description='Userspace I/O in Python, for controlling PRUS on the BeagleBone',
      author='Matthijs van Duin',
      author_email='',
      license='MIT',
      url='https://github.com/mvduin/py-uio',
      packages=find_packages()
      )
