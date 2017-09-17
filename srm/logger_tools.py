#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


import logging

from srm.file_operations import get_full_path


def setup_console_logger(str_format="%(levelname)s: %(message)s", level=logging.INFO):
    """
    Setup console logger.
    """
    root_logger = logging.getLogger()
    formatter = logging.Formatter(str_format)

    shandler = logging.StreamHandler()
    shandler.setLevel(level)
    shandler.setFormatter(formatter)

    root_logger.addHandler(shandler)
    root_logger.setLevel(level)


def setup_file_logger(filename="", str_format="%(levelname)s: %(message)s", level=logging.INFO):
    """Setup file logger"""
    root_logger = logging.getLogger()
    formatter = logging.Formatter(str_format)

    fhandler = logging.FileHandler(get_full_path(filename))
    fhandler.setLevel(level)
    fhandler.setFormatter(formatter)

    root_logger.addHandler(fhandler)
    root_logger.setLevel(level)
