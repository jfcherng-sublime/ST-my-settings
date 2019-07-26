#!/usr/bin/python
# -*- coding: utf-8 -*-


class SimpleWSServer(object):

    """SimpleWSServer"""

    def __init__(self):
        try:
            if not self.ws_callbacks:
                self.ws_callbacks = []
        except Exception:
            self.ws_callbacks = []

    def has_ws_callback(self, path):
        """Traverse added static_files return object"""

        for callback in self.ws_callbacks:
            if path in callback["path"]:
                return callback
        return False
