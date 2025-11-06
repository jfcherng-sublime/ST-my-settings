from typing import Any, Dict
import sublime
import sublime_plugin


class MyTextInputHandlerDemoCommand(sublime_plugin.TextCommand):
    def __init__(self, view: sublime.View) -> None:
        self.view = view
        self.input_handler = MyTestInputHandler()

    def input(self, args: dict[str, Any] = {}) -> sublime_plugin.CommandInputHandler:
        return self.input_handler

    def run(self, edit: sublime.Edit, **args: dict[str, Any]) -> None:
        print(f"{self.name()} run args: {args}")

        if self.input_handler.name() in args:
            return

        self.view.window().run_command("show_overlay", {"overlay": "command_palette", "command": self.name()})

    def input_description(self) -> str:
        return "Here's input_description"


class MyTestInputHandler(sublime_plugin.TextInputHandler):
    def placeholder(self) -> str:
        return "Here's placeholder"

    def preview(self, text: str) -> sublime.Html:
        return sublime.Html(
            f"<b>{text[:2]}</b> / <i>{text[2:4]}</i> / <u>{text[4:6]}</u> / {text[6:]}"
            + '<a href="https://google.com">Link to Google</a>'
            + '<br><span style="color:red">Here is a new line</span>'
        )

    def validate(self, text: str) -> bool:
        is_valid = text == "pass"

        if not is_valid:
            sublime.error_message(f"invalid input: {text}")

        return is_valid

    def cancel(self) -> None:
        sublime.message_dialog("canceled")

    def confirm(self, text: str) -> None:
        sublime.message_dialog(f"confirmed: {text}")

    def description(self, text: str) -> str:
        return f"My command description: {text}"
