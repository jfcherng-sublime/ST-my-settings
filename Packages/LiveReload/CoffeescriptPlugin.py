#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import threading
import subprocess
import sys
import sublime
import sublime_plugin

# fix for import order

sys.path.append(os.path.join(sublime.packages_path(), "LiveReload"))
LiveReload = __import__("LiveReload")
sys.path.remove(os.path.join(sublime.packages_path(), "LiveReload"))


class CoffeeThread(threading.Thread):
    def getLocalOverride(self):
        """
        You can override defaults in sublime-project file
        
        Discussion: https://github.com/dz0ny/LiveReload-sublimetext2/issues/43
        
        Example: 

            "settings": {
              "coffee": {
                "command": "coffee -cv --maps"
              }
            }
        """
        try:
            view_settings = sublime.active_window().active_view().settings()
            view_settings = view_settings.get("lrcoffee")
            if view_settings:
                return view_settings
            else:
                return {}
        except Exception:
            return {}

    def __init__(self, dirname, on_compile, filename):

        self.filename = filename

        ##TODO: Proper handler for this
        try:
            self.dirname = self.getLocalOverride.get("dirname") or dirname.replace(
                "\\", "/"
            )
        except Exception as e:
            self.dirname = dirname.replace("\\", "/")
        try:
            self.command = self.getLocalOverride.get("command") or "coffee -c"
        except Exception as e:
            self.command = "coffee -c"

        self.stdout = None
        self.stderr = None
        self.on_compile = on_compile
        threading.Thread.__init__(self)

    def run(self):
        cmd = (
            self.command
            + " "
            + self.filename
            + " "
            + self.filename.replace(".coffee", ".js")
        )

        p = subprocess.Popen(
            cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        test = p.stdout.read()
        # if there is no result, everything worked Great!
        if not test:
            self.on_compile()
        else:
            # something went wrong...
            err = test.split("\n")
            sublime.error_message(err[0])


class coffeePreprocessor(LiveReload.Plugin, sublime_plugin.EventListener):

    title = "CoffeeScript Preprocessor"
    description = "Coffeescript Compile and refresh page, when file is compiled"
    file_types = ".coffee"
    this_session_only = True
    file_name = ""

    def on_post_save(self, view):
        self.original_filename = os.path.basename(view.file_name())

        if self.should_run(self.original_filename):
            self.file_name_to_refresh = self.original_filename.replace(".coffee", ".js")
            dirname = os.path.dirname(view.file_name())
            CoffeeThread(dirname, self.on_compile, self.original_filename).start()

    def on_compile(self):
        print(self.file_name_to_refresh)
        settings = {
            "path": self.file_name_to_refresh,
            "apply_js_live": False,
            "apply_css_live": False,
            "apply_images_live": False,
        }
        self.sendCommand("refresh", settings, self.original_filename)
