#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
from os.path import join, dirname

import srm

setup(
    name="srm",
    version=srm.__version__,
    test_suite='tests',
    packages=find_packages(),
    description="smart RM",
    author="Miroslav Ganevich",
    author_email="miroslav_ganevich@mail.com",
    url="https://github.com/GitMaster97/srm",
    long_description=open(join(dirname(__file__), 'README.md')).read(),
    entry_points={
        'console_scripts':
            ['srm = srm.main:main']
        }
)