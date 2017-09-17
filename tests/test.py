#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


import unittest
import os
import re
import datetime
import time

from srm.file_operations import create_path, clear_dir
from srm.wastebasket_manager import WasteBasketManager
from srm.move_error import MoveError


class TestWasteBasketRemove(unittest.TestCase):
    def setUp(self):
        self.wbm = WasteBasketManager(wastebasket_path="Trash_TEST")
        self.paths = [
            "srm_test/remove_me.txt",
            "srm_test/and_me.txt",
            "srm_test/me_too.txt",
            "srm_test/v_a",
            "srm_test/v_b",
            "srm_test/v_c",
            "srm_test/dir/123.txt",
            "srm_test/dir/four.txt",
            "srm_test/dir/five",
            "srm_test/dir/cX.notxt",
            "srm_test/dir/a/.shhhh",
            "srm_test/.shh",
            "srm_test/empty_dir/"
            ]

        for path in self.paths:
            is_file = not path.endswith("/")
            create_path(path, is_file=is_file)

    def tearDown(self):
        clear_dir("srm_test")
        os.rmdir("srm_test")

        clear_dir("Trash_TEST")
        os.rmdir("Trash_TEST")


    def test_remove_existing_files(self):
        """
        Tests for the presence of a file in the WasteBasket and dictionary.
        """
        self.wbm.rmdir = True
        self.wbm.remove(*self.paths)

        for path in self.paths:
            trash_name = os.path.basename(path) + ".0"
            if path.endswith('/'):
                trash_name = os.path.basename(os.path.dirname(path)) + ".0"

            path = os.path.join(self.wbm.file_dir, trash_name)
            self.assertTrue(os.path.exists(path))
            self.assertTrue(self.wbm.trashinfo.get(trash_name))


    def test_remove_nonexisting_files(self):
        """
        Tests if an exception has been raise.
        """
        with self.assertRaises(MoveError):
            self.wbm.remove("/ghost_file")


    def test_remove_empty_dir(self):
        self.wbm.rmdir = True
        self.wbm.remove("srm_test/empty_dir")

        path = os.path.join(self.wbm.file_dir, "empty_dir.0")

        self.assertTrue(os.path.exists(path))
        self.assertTrue(self.wbm.trashinfo.get("empty_dir.0"))


    def test_remove_file(self):
        self.wbm.remove("srm_test/remove_me.txt")

        path = os.path.join(self.wbm.file_dir, "remove_me.txt.0")

        self.assertTrue(os.path.exists(path))
        self.assertTrue(self.wbm.trashinfo.get("remove_me.txt.0"))


    def test_remove_regex_search_dirs(self):
        """
        Tests for the presence of a file in the WasteBasket and dictionary.
        Tests for match by pattern.
        """
        self.wbm.remove_regex("srm_test/.txt$", search_dirs=True)

        for path in self.paths:
            if re.match(r".txt$", path):
                trash_name = os.path.basename(path) + ".0"
                path = os.path.join(self.wbm.file_dir, trash_name)

                self.assertTrue(os.path.exists(path))
                self.assertTrue(self.wbm.trashinfo.get(trash_name))


    def test_remove_regex_not_search_dirs(self):
        """
        Tests for the presence of a file in the WasteBasket and dictionary.
        Tests for match by pattern.
        """
        self.wbm.remove_regex("srm_test/.txt$")

        for path in self.paths:
            if re.match(r".txt$", path) and os.path.dirname(path) == "srm_test":
                trash_name = os.path.basename(path) + ".0"
                path = os.path.join(self.wbm.file_dir, trash_name)

                self.assertTrue(os.path.exists(path))
                self.assertTrue(self.wbm.trashinfo.get(trash_name))


    def test_restore_existing_file(self):
        for path in os.listdir("srm_test"):
            path = os.path.join("srm_test", path)
            self.wbm.rmdir = True
            self.wbm.remove(path)

        trash_items = ["and_me.txt", "me_too.txt", "v_a",
                       "v_b", "v_c", "dir", ".shh", "empty_dir"]
        self.wbm.restore(*[name + ".0" for name in trash_items])

        for path in trash_items:
            self.assertTrue(os.path.exists(os.path.join("srm_test", path)))


    def test_restore_nonexisting_file(self):
        for path in os.listdir("srm_test"):
            path = os.path.join("srm_test", path)
            self.wbm.rmdir = True
            self.wbm.remove(path)

        trash_items = ["asd.txt", "measdf_too.txt", "vdd_a",
                       "vff_b", "vss_c", "ffff", ".sh222h"]
        with self.assertRaises(IOError):
            self.wbm.restore(*[i + ".0" for i in trash_items])


    def test_restore_merge_case(self):
        self.wbm.rmdir = True
        self.wbm.remove("srm_test/dir")
        create_path("srm_test/dir/some_file", is_file=True)
        create_path("srm_test/dir/some", is_file=True)
        create_path("srm_test/dir/file", is_file=True)
        create_path("srm_test/dir/SoM", is_file=True)
        self.paths.append("srm_test/dir/some_file")
        self.paths.append("srm_test/dir/some")
        self.paths.append("srm_test/dir/file")
        self.paths.append("srm_test/dir/SoM")

        self.wbm.restore("dir.0")

        for path in self.paths:
            self.assertTrue(os.path.exists(path))


    def test_restore_empty_dir(self):
        self.wbm.rmdir = True
        self.wbm.remove("srm_test/empty_dir")
        self.wbm.restore("empty_dir.0")


        path = os.path.join(self.wbm.file_dir, "empty_dir.0")

        self.assertFalse(os.path.exists(path))
        self.assertTrue(os.path.exists("srm_test/empty_dir/"))

        with self.assertRaises(IOError):
            self.wbm.trashinfo.get("empty_dir.0")


    def test_restore_file(self):
        self.wbm.remove("srm_test/remove_me.txt")
        self.wbm.restore("remove_me.txt.0")

        path = os.path.join(self.wbm.file_dir, "remove_me.txt.0")

        self.assertFalse(os.path.exists(path))
        self.assertTrue(os.path.exists("srm_test/remove_me.txt"))

        with self.assertRaises(IOError):
            self.wbm.trashinfo.get("remove_me.txt.0")


    def test_time_policy(self):
        self.wbm.storage_time = datetime.timedelta(seconds=1)
        self.wbm.rmdir = True
        self.wbm.remove(*self.paths)

        for path in self.paths:
            self.assertFalse(os.path.exists(path))
        
        time.sleep(1)
        removed_files = self.wbm.clear_by_time_policy()
        
        self.assertFalse(os.listdir(self.wbm.trashinfo_dir))
        self.assertFalse(os.listdir(self.wbm.file_dir))
    

    def test_size_policy(self):
        self.wbm.rmdir = True
        self.wbm.remove(*self.paths)
        self.wbm.max_size = 0

        self.wbm.clear_by_size_policy()

        self.assertFalse(os.listdir(self.wbm.trashinfo_dir))
        self.assertFalse(os.listdir(self.wbm.file_dir))


def main():
    """
    Run tests
    """
    unittest.main()

if __name__ == '__main__':
    main()
