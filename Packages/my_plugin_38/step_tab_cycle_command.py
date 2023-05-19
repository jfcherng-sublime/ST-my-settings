"""
Modified from https://github.com/ahuff44/sublime-better-tab-cycling

Keybinding example:

// go to the previous tab sheet
{ "keys": ["ctrl+super+j"], "command": "step_tab_cycle", "args": { "steps": -1 } },
// go to the next tab sheet
{ "keys": ["ctrl+super+l"], "command": "step_tab_cycle", "args": { "steps": 1 } },
"""
from __future__ import annotations

import sublime_plugin


class StepTabCycleCommand(sublime_plugin.WindowCommand):
    """
    Switch to the next tab in the active pane.
    Like sublime's builtin next_sheet, but stays within the active pane
    """

    def run(self, steps: int) -> None:
        window = self.window

        if not (sheet := window.active_sheet()):
            return

        group_index, sheet_index = window.get_sheet_index(sheet)
        sheets = window.sheets_in_group(group_index)
        sheet_index_focus = (sheet_index + steps) % len(sheets)
        window.focus_sheet(sheets[sheet_index_focus])
