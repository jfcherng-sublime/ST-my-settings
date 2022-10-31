import sublime
import sublime_plugin


class AlwaysIndentCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        for sel in reversed(self.view.sel()):
            for line in reversed(self.view.lines(sel)):
                self.view.insert(edit, line.begin(), "\t")
