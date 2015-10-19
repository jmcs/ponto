#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = '0.0.0dev1'

setup(
    name='ponto',
    packages=find_packages(),
    version=version,
    description='Backup Manager',
    author='João Santos',
    url='https://github.com/jmcs/ponto',
    license='MIT License',
    install_requires=['click', 'pathlib', 'clickclick', 'requests', 'pip'],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
    ],
    long_description='Git Backed Backup Manager',
    entry_points={'console_scripts': ['ponto = ponto.cli:cli']}
)
