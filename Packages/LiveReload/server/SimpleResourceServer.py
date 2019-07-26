#!/usr/bin/python
# -*- coding: utf-8 -*-


class SimpleResourceServer(object):

    """SimpleResourceServer"""

    def __init__(self):
        self.static_files = []

    def has_file(self, path):
        """Traverse added static_files return object"""

        for l_file in self.static_files:
            if path == l_file["path"]:
                return l_file
        return False
