#!/usr/bin/python
# -*- coding: utf-8 -*-


class SimpleCallbackServer(object):

    """SimpleCallbackServer"""

    def __init__(self):
        try:
            if not self.callbacks:
                self.callbacks = []
        except Exception:
            self.callbacks = []

    def has_callback(self, path):
        """Traverse added static_files return object"""

        for callback in self.callbacks:
            if path in callback["path"]:
                print(self.callbacks)
                print(path)
                return callback
        return False
