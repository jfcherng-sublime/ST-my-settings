from typing import List

import sublime
import sublime_plugin


class ExtendSelectionToPreviousLineCommand(sublime_plugin.TextCommand):
    """
    Similar to `ctrl+l` but the selection is upward.

    Recommended keybinding:
    ```js
    { "keys": ["..."], "command": "extend_selection_to_previous_line" },
    ```
    """

    def run(self, edit: sublime.Edit) -> None:
        v = self.view
        sel = v.sel()

        regions: List[sublime.Region] = []
        for r in sel:
            row, col = v.rowcol(old_end := r.end())
            new_begin = max(old_end, v.line(r).end()) if col else old_end

            row, col = v.rowcol(old_begin := r.begin())
            new_end = v.text_point(row + 1, 0) if col else old_begin

            regions.append(sublime.Region(new_begin, new_end))

        sel.clear()
        sel.add_all(regions)

        v.run_command("move", {"by": "lines", "extend": True, "forward": False})
