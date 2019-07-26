#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import sublime
import sublime_plugin

# fix for import order

sys.path.append(os.path.join(sublime.packages_path(), "LiveReload"))
LiveReload = __import__("LiveReload")
sys.path.remove(os.path.join(sublime.packages_path(), "LiveReload"))


class SimpleRefresh(LiveReload.Plugin, sublime_plugin.EventListener):

    title = "Simple Reload"
    description = "Refresh page, when file is saved"
    file_types = "*"

    def on_post_save(self, view):
        self.refresh(os.path.basename(view.file_name()))
