#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


import json
import logging
import os
import pytoml

from srm.file_operations import get_full_path, create_path
from srm.remove_policy import RemovePolicy


DEFAULT_CONFIG = {
    "cleaning_policy": RemovePolicy.SIZE,
    "clear": False,
    "content": False,
    "dry_run": False,
    "force": False,
    "in_lines": False,
    "max_size": 4.0,
    "regex": False,
    "restore": False,
    "rmdir": False,
    "short": False,
    "silent": False,
    "storage_time": "30 days, 0:0:0",
    "wastebasket_path": "~/Trash"
}


def create_config(path, config_dict=None):
    """
    Create config file.
    """
    if config_dict is None:
        config_dict = {}

    file_extension = os.path.splitext(path)[-1]
    path = get_full_path(path)

    if not os.path.exists(path):
        create_path(path, is_file=True)

    with open(path, 'w') as config_file:
        if file_extension == ".json":
            json.dump(config_dict, config_file, indent=4, sort_keys=True)
        elif file_extension == ".toml":
            pytoml.dump(config_dict, config_file, sort_keys=True)
        else:
            warning_message = """"{file}" has not been created!
It has a format different from json and toml.""".format(file=path)
            logging.warning(warning_message)


def load_config(path):
    """
     Load config file and return configuration parameters dict.
     """
    path = get_full_path(path)
    file_extension = os.path.splitext(path)[-1]
    config = DEFAULT_CONFIG

    if not os.path.exists(path):
        warning_message = """The "{file}" does not exist!
The default config will be used.""".format(file=path)

        logging.warning(warning_message)
        return config

    with open(path, 'r') as config_file:
        if file_extension == ".json":
            config = json.load(config_file)
        elif file_extension == ".toml":
            config = pytoml.load(config_file)
        else:
            warning_message = """The "{file}" does not match the format of toml in json!
The default config will be used.""".format(file=path)
            logging.warning(warning_message)

    return config


def update_config(path="", config_dict=None):
    """
    Update current config file
    """
    if config_dict is None:
        config_dict = {}

    path = get_full_path(path)
    file_extension = os.path.splitext(path)[-1]

    if not os.path.exists(path):
        warning_message = """The "{file}" does not exist!""".format(file=path)
        logging.warning(warning_message)
        return

    with open(path, 'w') as config_file:
        if file_extension == ".json":
            json.dump(config_dict, config_file, indent=4, sort_keys=True)
        elif file_extension == ".toml":
            pytoml.dump(config_dict, config_file, sort_keys=True)
        else:
            warning_message = """"{file}" has not been updated!
It has a format different from json and toml.""".format(file=path)
            logging.warning(warning_message)


def cat_config(path):
    """
    Shows config file content
    """
    path = get_full_path(path)

    with open(path, "r") as config_file:
        config_file_lines = config_file.readlines()

    config_string_representation = '"{file}":\n'.format(file=path)
    for line in config_file_lines:
        config_string_representation += "\t{line}".format(line=line)

    logging.info(config_string_representation)
