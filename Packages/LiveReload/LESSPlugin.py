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


class LessThread(threading.Thread):
    def getLocalOverride(self):
        """
        You can override defaults in sublime-project file
        
        Discussion: https://github.com/dz0ny/LiveReload-sublimetext2/issues/43
        
        Example: 

            "settings": {
              "lesscompass": {
                "command": "compass compile -e production --force"
              }
            }
        """
        try:
            view_settings = sublime.active_window().active_view().settings()
            view_settings = view_settings.get("lrless")
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
            # print(e)
        try:
            self.command = self.getLocalOverride.get("command") or "lessc --verbose"
        except Exception as e:
            self.command = "lessc --verbose"
            # print(e)

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
            + self.filename.replace(".less", ".css")
        )

        p = subprocess.Popen(
            cmd,
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        test = p.stdout.read()
        if test:
            print("ATSDFASDFASDFASD!!")
            print(test)
            self.on_compile()


class lessPreprocessor(LiveReload.Plugin, sublime_plugin.EventListener):

    title = "Less Preprocessor"
    description = "Less Compile and refresh page, when file is compiled"
    file_types = ".less"
    this_session_only = True
    file_name = ""

    def on_post_save(self, view):
        self.original_filename = os.path.basename(view.file_name())

        if self.should_run(self.original_filename):
            self.file_name_to_refresh = self.original_filename.replace(".less", ".css")
            dirname = os.path.dirname(view.file_name())
            LessThread(dirname, self.on_compile, self.original_filename).start()

    def on_compile(self):
        print(self.file_name_to_refresh)
        settings = {
            "path": self.file_name_to_refresh,
            "apply_js_live": False,
            "apply_css_live": True,
            "apply_images_live": True,
        }
        self.sendCommand("refresh", settings, self.original_filename)
