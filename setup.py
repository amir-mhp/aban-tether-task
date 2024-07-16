#!/usr/bin/env python
from setuptools import find_packages, setup

setup(
    name='core',
    version='1.0.0',
    description='Core for Aban Tether Task',
    packages=find_packages(exclude=['test', 'test.*']),
    zip_safe=True
)
