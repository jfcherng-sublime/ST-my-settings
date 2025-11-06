from __future__ import annotations

import sublime_plugin


class FocusActiveOutputPanelCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        if not (panel_name := self.window.active_panel()):
            return

        self.window.run_command("show_panel", {"panel": panel_name})

        if not panel_name.startswith("output."):
            return

        panel_name = panel_name[len("output.") :]
        panel = self.window.find_output_panel(panel_name)
        assert panel
        self.window.focus_view(panel)
