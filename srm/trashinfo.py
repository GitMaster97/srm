#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import json
import datetime
import os

from srm.file_operations import get_full_path, clear_dir


TRASHINFO_PATH = os.path.expanduser("~/.info.json")


class TrashInfo(object):
    """
    The class provides information about the deleted files.

    Attention! Do not work directly with the _files_dict!
    Use methods of push, pop and clear for work with it.
    """

    def __init__(self, trashinfo_path=TRASHINFO_PATH):
        self.trashinfo_path = get_full_path(trashinfo_path)


    def content(self):
        """Return list of full path trashinfo items."""
        return [os.path.join(self.trashinfo_path, filename) for filename in os.listdir(self.trashinfo_path)]


    def push(self, path):
        """
        Created trashinfo element. Return filename in trashinfo.
        """
        deletion_date = datetime.datetime.now()
        old_path = get_full_path(path)

        filename = os.path.basename(old_path)
        index = 0

        unique_name = "{filename}.{index}".format(filename=filename, index=index)
        trashinfo_list = os.listdir(self.trashinfo_path)

        while unique_name in trashinfo_list:
            index += 1
            unique_name = "{filename}.{index}".format(filename=filename, index=index)

        trashinfo = {
            "old path": old_path,
            "deletion date": deletion_date.strftime("%Y-%m-%dT%H:%M:%S")
            }
        trashinfo_filename = os.path.join(self.trashinfo_path, unique_name)

        with open(trashinfo_filename, 'w') as trashinfo_file:
            json.dump(trashinfo, trashinfo_file)

        return unique_name


    def pop(self, name):
        """
        Return trashinfo for a given name or raise KeyError if don't exist.
        """
        trashinfo = self.get(name)
        
        full_path_to_trashinfo_file = os.path.join(self.trashinfo_path, name)
        os.remove(full_path_to_trashinfo_file)

        return trashinfo


    def get(self, name):
        """
        Get trashinfo for a given name or raice IOError if don't exist.
        """
        full_path_to_trashinfo_file = os.path.join(self.trashinfo_path, name)

        trashinfo = None
        with open(full_path_to_trashinfo_file, 'r') as trashinfo_file:
            trashinfo = json.load(trashinfo_file)
        
        return trashinfo


    def clear(self):
        """
        Clear trashinfo dir
        """
        clear_dir(self.trashinfo_path)
