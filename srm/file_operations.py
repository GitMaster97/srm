#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os


def move(src, dst, dry_run=False):
    """
    Moves from src to dst.
    """
    src = get_full_path(src)
    dst = get_full_path(dst)

    if not dry_run:
        if os.path.exists(dst) and os.path.isdir(dst) and os.path.isdir(src):
            merge_dirs(src, dst)
        else:
            os.rename(src, dst)

    return (src, dst)


def merge_dirs(src, dst):
    """
    Merge dirs, replace all files in dst with files from src
    """
    for node in os.listdir(src):
        current_dst = os.path.join(dst, node)
        node = os.path.join(src, node)

        if os.path.isfile(node):
            if os.path.exists(current_dst):
                os.remove(current_dst)
            os.rename(node, current_dst)

        if os.path.isdir(node):
            if not os.path.exists(current_dst):
                os.mkdir(current_dst)
            merge_dirs(node, current_dst)

    if os.path.exists(src):
        os.rmdir(src)


def get_full_path(path):
    """
    Return full path to file.
    """
    return os.path.abspath(os.path.expanduser(path))


def create_path(path, is_file=False):
    """
    Takes the full path to the directory or file,
    if last_dir is False and creates it.

    OSError will be raiced if current user have not access.
    """
    path = get_full_path(path)
    if is_file:
        if not os.path.exists(os.path.dirname(path)):
            os.makedirs(os.path.dirname(path))
        os.mknod(path)
    elif not os.path.exists(path):
        os.makedirs(path)


def get_dir_size(directory):
    """
    Returns the total amount of space occupied by files in the dir.
    """
    total_size = 0

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if not os.path.islink(file_path):
                total_size += os.path.getsize(file_path)
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.path.islink(dir_path):
                total_size += os.path.getsize(dir_path)

    return total_size


def clear_dir(directory):
    """
    Recursively deletes all files in the specified directory
    """
    for node in os.listdir(directory):
        full_path = os.path.join(directory, node)

        if os.path.isfile(full_path) or os.path.islink(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            clear_dir(full_path)
            os.rmdir(full_path)

def cut_leafs(*tree):
    """
    Returns a tuple of lists (parents, leafs).

    parents - list of path tree without leafs
    leafs   - list of path that do not have descendants in current tree
    """
    tree = list(tree)
    tree.sort()
    parents, leafs = [], []
    for i in xrange(len(tree)):
        if i+1 < len(tree) and tree[i+1].startswith(tree[i]):
            parents.append(tree[i])
        else:
            leafs.append(tree[i])
    return (parents, leafs)