from __future__ import annotations

import sublime
import sublime_plugin


class RunAsyncCommand(sublime_plugin.WindowCommand):
    """Run a given command asynchronously."""

    def run(self, command: str, args: dict = {}, timeout_ms: float = 0) -> None:
        sublime.set_timeout_async(lambda: self.window.run_command(command, args), timeout_ms)
