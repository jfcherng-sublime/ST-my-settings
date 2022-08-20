from typing import Tuple

import sublime
import sublime_plugin


class ToggleAllInlineDiffsCommand(sublime_plugin.TextCommand):
    """A command to toggle all inline diffs in a view."""

    def run(self, edit: sublime.Edit) -> None:
        sel = self.view.sel()
        regions_backup: Tuple[sublime.Region, ...] = tuple(sel)

        # toggle the whole file inline diff
        sel.clear()
        sel.add(sublime.Region(0, self.view.size()))
        self.view.run_command("toggle_inline_diff", {"args": {"prefer_hide": True}})

        # add back previous selection
        sel.clear()
        sel.add_all(regions_backup)
