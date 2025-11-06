from __future__ import annotations
from collections.abc import Sequence

import getpass
import os
import shlex
import subprocess
import tempfile
import traceback
from collections import UserDict
from datetime import datetime
from pathlib import Path
from typing import Any, TypeVar

import sublime
import sublime_plugin

T_ExpandableVar = TypeVar("T_ExpandableVar", None, bool, int, float, str, dict, list, tuple)


class SyntaxMapping(UserDict):
    def resolve(self, key: Any) -> str | None:
        visited = {None}
        while (syntax := self.get(key)) not in visited:
            if isinstance(syntax, str):
                return syntax
            visited.add(key := syntax)
        return None


SYNTAX_MAPPING = SyntaxMapping(
    {
        ("git", "blame"): "scope:text.git-blame",
        ("git", "diff"): "scope:source.diff",
        ("git", "log"): "scope:text.git.log",
        ("git", "show"): "scope:source.diff",
        ("git", "status"): "scope:source.diff",
        # aliases
        ("git", "bl"): ("git", "blame"),
        ("git", "d"): ("git", "diff"),
        ("git", "sh"): ("git", "show"),
        ("git", "st"): ("git", "status"),
    }
)


def empty_view_text(view: sublime.View) -> None:
    view.run_command("select_all")
    view.run_command("left_delete")


def replace_view_text(view: sublime.View, text: str) -> None:
    empty_view_text(view)
    append_view_text(view, text)


def append_view_text(view: sublime.View, text: str) -> None:
    view.run_command("append", {"characters": text})


def expand_variables(
    window: sublime.Window,
    value: T_ExpandableVar,
    *,
    extra: dict[str, Any] | None = None,
) -> T_ExpandableVar:
    variables = window.extract_variables()
    variables.update(
        {
            "home": os.path.expanduser("~"),
            "temp": tempfile.gettempdir(),
            **(extra or {}),
        }
    )

    return sublime.expand_variables(value, variables)


def find_view_project_root(view: sublime.View) -> str | None:
    if (
        not (window := view.window())
        or not (filepath := view.file_name())
        or not (project_roots := window.folders())
        # ...
    ):
        return None

    if os.name == "nt":
        # fix drive cases
        filepath = Path(filepath).resolve().as_posix() + "/"
        roots = tuple(Path(root).resolve().as_posix() + "/" for root in project_roots)
    else:
        roots = project_roots

    return next(filter(filepath.startswith, roots), None)


def lookup_cmd_syntax(cmd: str) -> str | None:
    cmd_parts = shlex.split(cmd)
    for prefix in SYNTAX_MAPPING:
        if sequence_startswith(cmd_parts, prefix):
            return SYNTAX_MAPPING.resolve(prefix)
    return None


def sequence_startswith(seq: Sequence[str], prefix: Sequence[str]) -> bool:
    return all(seq[i] == prefix[i] for i in range(len(prefix)))


def run_cli_command(
    cmd: str | Sequence[str],
    cwd: str = "",
    encoding: str = "utf-8",
    timeout_s: float | None = None,
    shell: bool = False,
) -> tuple[str, str, int]:
    if os.name == "nt":
        # do not create a window for the process
        startupinfo = subprocess.STARTUPINFO()  # type: ignore
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW  # type: ignore
        startupinfo.wShowWindow = subprocess.SW_HIDE  # type: ignore
    else:
        startupinfo = None  # type: ignore

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        encoding=encoding,
        startupinfo=startupinfo,
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
        shell=shell,
        text=True,
    )

    stdout, stderr = process.communicate(timeout=timeout_s)
    ret_code = process.poll() or 0

    return stdout, stderr, ret_code


def get_cli_command_result_text(
    cmd: str | Sequence[str],
    cwd: str = "",
    encoding: str = "utf-8",
    timeout_s: float | None = None,
    shell: bool = False,
) -> str:
    stdout, stderr, _ = run_cli_command(cmd, cwd=cwd, encoding=encoding, timeout_s=timeout_s, shell=shell)

    output = ""
    if stdout:
        output += stdout + "\n" * 3
    if stderr:
        output += stderr + "\n" * 3
    output = output.rstrip() + "\n"

    return "" if output.isspace() else output


class CliRunnerCommand(sublime_plugin.WindowCommand):
    def run(
        self,
        cwd: str = "",
        initial_text: str = "",
        encoding: str = "utf-8",
        shell: bool = False,
    ) -> None:
        if not (view := self.window.active_view()):
            sublime.error_message("No active view")
            return

        if file_name := view.file_name():
            file_dir = str(Path(file_name).parent)
        else:
            file_dir = None

        if not cwd:
            if project_root := find_view_project_root(view):
                cwd = project_root
            else:
                dirs: list[str] = []
                if file_name:
                    dirs.append(os.path.dirname(file_name))
                dirs.append("${home}")
                cwd = dirs[0]

        self.shell = shell
        self.cwd = self.fix_cwd_unc(expand_variables(self.window, cwd, extra={"file_dir": file_dir or "\0"}))
        self.encoding = encoding

        self.window.show_input_panel(f"[{getpass.getuser()}@{self.cwd}]", initial_text, self.on_done, None, None)

    def on_done(self, cmd: str) -> None:
        if not cmd:
            return

        sublime.set_timeout_async(
            lambda: self.window.run_command(
                "cli_runner_show_result",
                {
                    "cmd": cmd,
                    "cwd": self.cwd,
                    "encoding": self.encoding,
                    "shell": self.shell,
                },
            )
        )

    @staticmethod
    def fix_cwd_unc(path: str) -> str:
        """
        To deal with an escaping "bug" in `sublime.expand_variables()` for UNC path.

        @see https://github.com/sublimehq/sublime_text/issues/1878
        """
        if path.startswith("\\"):
            path = r"\\" + path.lstrip("\\")
        return path


class CliRunnerShowResultCommand(sublime_plugin.TextCommand):
    VIEW_MARK = "is_from_cli_runner"

    def is_visible(self) -> bool:
        return False

    def run(
        self,
        edit: sublime.Edit,
        cmd: str | None = None,
        cwd: str = "",
        encoding: str = "utf-8",
        shell: bool = False,
    ) -> None:
        is_in_cmd_view = self.view.settings().get(self.VIEW_MARK)
        now = datetime.now()

        if is_in_cmd_view:
            view = self.view
            settings = view.settings()

            cmd = settings.get("cli_runner.cmd")
            cwd = settings.get("cli_runner.cwd")
            encoding = settings.get("cli_runner.encoding")
            shell = settings.get("cli_runner.shell")
        else:
            if not (window := self.view.window()):
                return
            view = window.new_file()

        if not cmd:
            return

        sublime.status_message(f"Re-run command: {cmd}")
        try:
            output = get_cli_command_result_text(cmd, cwd=cwd, encoding=encoding, shell=shell)
        except Exception:
            output = traceback.format_exc()

        if not (syntax := lookup_cmd_syntax(cmd)):
            first_line = output[:200].partition("\n")[0]
            syntax = getattr(sublime.find_syntax_for_file("", first_line), "path", "scope:text.plain")

        view.set_scratch(True)
        view.set_name(f'({now.strftime("%Y%m%d%H%M%S")}) {cmd}')
        view.assign_syntax(syntax)
        view.settings().update(
            {
                self.VIEW_MARK: True,
                "cli_runner.cmd": cmd,
                "cli_runner.cwd": cwd,
                "cli_runner.encoding": encoding,
                "cli_runner.shell": shell,
                "cli_runner.timestamp": now.timestamp(),
            }
        )

        replace_view_text(view, output)
