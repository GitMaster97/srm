#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


"""
The module provides functions for working with the WasteBasket.
"""


import datetime
import re
import os
import json

from srm.file_operations import(
    clear_dir, move,
    get_full_path,
    create_path,
    get_dir_size
)
from srm.trashinfo import TrashInfo
from srm.move_error import MoveError


TRASHDIR_PATH = os.path.expanduser("~/Trash")
MAX_SIZE = 32
STORAGE_TIME = datetime.timedelta(days=30)


class WasteBasketManager(object):
    """
    The object of this class provides methods for working with the WasteBasket.

    Arguments:
        dry_run - if set, simulates the operation of the object, no changes are applied
        rmdir   - if set, removes dirs, otherwise raise OSError;
        force   - if set, ignore Exceptions and continue work;


        max_size     - sets the maximum WasteBasket size, if exceeded, clears it
                       WasteBasket capacity indicated in GB

        storage_time - sets the storage time of the trash items, if exceeded, clears it


        wastebasket_path - specifies the path to the WasteBasket directory.
                           If it does not exist, сreates it
    """

    def __init__(self, dry_run=False, force=False, rmdir=False,
                 max_size=MAX_SIZE, storage_time=STORAGE_TIME,
                 wastebasket_path=TRASHDIR_PATH): 
        self.dry_run = dry_run
        self.rmdir = rmdir
        self.force = force

        self.wastebasket_path = wastebasket_path
        self.trashinfo_dir = os.path.join(self.wastebasket_path, "info/")
        self.file_dir = os.path.join(self.wastebasket_path, "files/")

        self.create_wastebasket(self.wastebasket_path)
        self.trashinfo = TrashInfo(self.trashinfo_dir)

        self.max_size = max_size * (1024 ** 3)
        self.storage_time = storage_time


    def create_wastebasket(self, path):
        """
        Creates wastebasket by the specified path.
        """
        self.wastebasket_path = get_full_path(path)
        
        if not os.path.exists(self.wastebasket_path):
            create_path(self.wastebasket_path)
        if not os.path.exists(self.file_dir):
            create_path(self.file_dir)
        if not os.path.exists(self.trashinfo_dir):
            create_path(self.trashinfo_dir)


    # Remove methods
    def remove(self, *paths):
        """
        Remove directories and files in WasteBasket.

        Returns a list of successfully moved files. The list item contains a
        tuple from the old and new paths.

        If path doesn't exist, OSError will be raised.
        """
        success_moved_files = []
        for path in paths:
            path = get_full_path(path)
            filename = self.trashinfo.push(path)

            try:
                if os.path.isdir(path) and not self.rmdir:
                    raise OSError(13, "Rmdir mode in not active")

                src_dst = move(path, os.path.join(self.file_dir, filename), dry_run=self.dry_run)
                success_moved_files.append(src_dst)

                if self.dry_run:
                    self.trashinfo.pop(filename) 

            except OSError as exception:
                self.trashinfo.pop(filename)
                if not self.force:
                    raise MoveError(message=exception.strerror,
                                    raised_path=path,
                                    success=success_moved_files)
        
        return success_moved_files


    def remove_regex(self, pattern, search_dirs=False):
        """
        Removes files by regex. Using breadth-first search.
        """
        full_pattern_path = get_full_path(pattern)
        pattern = os.path.basename(pattern)

        success_moved_files = []

        queue, visited_dirs = [], []
        queue.append(os.path.dirname(full_pattern_path))
        while queue:
            current_dir = queue.pop()
            visited_dirs.append(current_dir)

            for path in os.listdir(current_dir):
                if re.match(pattern, path):
                    path = os.path.join(current_dir, path)
                    src_dst = self.remove(path)
                    success_moved_files.extend(src_dst)

                    if os.path.isdir(path):
                        visited_dirs.append(path)

            if os.path.exists(current_dir):
                for path in os.listdir(current_dir):
                    full_path = os.path.join(current_dir, path)
                    if search_dirs and os.path.isdir(full_path) and full_path not in visited_dirs:
                        queue.insert(0, full_path)

        return success_moved_files


    # Restore methods
    def restore(self, *names):
        """
        Restore directories and files from WasteBasket
        """
        try:
            success_moved_files = []
            for name in names:
                trashinfo = self.trashinfo.get(name)

                restore_full_path = trashinfo["old path"]
                full_trashname = "{dir}{name}".format(dir=self.file_dir, name=name)

                create_path(os.path.dirname(restore_full_path))
                src_dst = move(full_trashname, restore_full_path, dry_run=self.dry_run)
                success_moved_files.append(src_dst)

                if not self.dry_run:
                    self.trashinfo.pop(name)
        except (KeyError, OSError) as exception:
            if not self.force:
                raise MoveError(message="No such file or directory",
                                raised_path=exception.args[0],
                                success=success_moved_files)

        return success_moved_files


    # Show method
    def content(self, short=True, in_lines=False):
        """
        Return list of files in WasteBasket.
        """
        return self.trashinfo.content()


    # Clear method
    def clear(self):
        """
        Removes all content from directories files/ and info
        """
        clear_dir(self.file_dir)
        self.trashinfo.clear()


    # Check methods
    def clear_by_size_policy(self):
        """
        Check the basket for cleaning by size.

           If the total WasteBasket volume is greater than the self.max_size
           then we clear the WasteBasket.

           Return True if WasteBasket was cleaned, else return False.
        """
        wastebasket_size = get_dir_size(self.file_dir)

        if wastebasket_size > self.max_size:
            self.clear()
            return True

        return False


    def clear_by_time_policy(self):
        """
        Check the basket for cleaning by time.

        If some file has a difference of its deletion time and
        the current time is greater than indicated in self.storage_time
        than this file will be deleted.

        Return list removable filenames.
        """
        removable_filenames = []
        for filename in self.trashinfo.content():
            with open(filename, 'r') as trashinfo_file:
                trashinfo = json.load(trashinfo_file)

            node_deletion_date = trashinfo["deletion date"]
            node_deletion_date = datetime.datetime.strptime(node_deletion_date, r"%Y-%m-%dT%H:%M:%S")

            delta_time = datetime.datetime.now() - node_deletion_date

            if delta_time > self.storage_time:
                removable_filenames.append(filename)

        for filename in removable_filenames:
            filename = os.path.basename(filename)
            path = os.path.join(self.file_dir, filename)
            
            if os.path.isfile(path):
                os.remove(path)
            else:
                clear_dir(path)
                os.rmdir(path)

            self.trashinfo.pop(filename)

        return removable_filenames
