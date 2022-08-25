import sublime
import sublime_plugin


class CopyWithoutNewlineCommand(sublime_plugin.TextCommand):
    def run(self, _: sublime.Edit) -> None:
        if self.view.has_non_empty_selection_region():
            self.view.run_command("copy")
            return

        sublime.set_clipboard(
            "\n".join(
                self.view.substr(self.view.line(r))
                for r in self.view.sel()
                # ...
            )
        )
