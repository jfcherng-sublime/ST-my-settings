# Sublime Deselect plugin
#
# based on a forum post by C0D312:
# https://www.sublimetext.com/forum/viewtopic.php?f=2&t=4716#p21219
from __future__ import annotations

import sublime
import sublime_plugin


class DeselectCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        if len(sel := self.view.sel()) == 0:
            return

        end = sel[0].b

        sel.clear()
        sel.add(end)
