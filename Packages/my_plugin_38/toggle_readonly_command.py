from typing import Any, Dict, Optional
import sublime
import sublime_plugin

STATUS_KEY = __file__


def update_status_bar(view: sublime.View) -> None:
    if view.is_read_only():
        view.set_status(STATUS_KEY, "🔒")
    else:
        view.erase_status(STATUS_KEY)


class ToggleReadOnlyCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, *, value: Any = None) -> None:
        if value is None:
            self.view.set_read_only(not self.view.is_read_only())
        else:
            self.view.set_read_only(bool(value))


class ReadOnlyStatusListener(sublime_plugin.ViewEventListener):
    def on_activated(self) -> None:
        update_status_bar(self.view)

    def on_post_text_command(self, command_name: str, args: Optional[Dict[str, Any]]) -> None:
        # why "revert" command makes the view read-only for a moment?
        if command_name not in {"revert"}:
            update_status_bar(self.view)
