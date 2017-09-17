#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-


class MoveError(Exception):
    def __init__(self, message="Move error",
                 raised_path=None,
                 success=None):
        self.message = message
        self.raised_path = raised_path
        self.success = success if success is not None else [] 

    def __str__(self):
        return '{msg}! "{path}" '.format(msg=self.message, path=self.raised_path)
