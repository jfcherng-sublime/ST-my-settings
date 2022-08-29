from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple, TypeVar, Union
import getpass
import os
import sublime
import sublime_plugin
import subprocess
import tempfile
import traceback

T_ExpandableVar = TypeVar("T_ExpandableVar", None, bool, int, float, str, Dict, List, Tuple)

SYNTAX_MAPPING = {
    "git bl": "scope:text.git-blame",
    "git blame": "scope:text.git-blame",
    "git d": "scope:source.diff",
    "git diff": "scope:source.diff",
    "git log": "scope:text.git.log",
    "git sh": "scope:source.diff",
    "git st": "scope:source.diff",
    "git status": "scope:source.diff",
}


def expand_variables(window: sublime.Window, value: T_ExpandableVar) -> T_ExpandableVar:
    variables = window.extract_variables()
    variables.update(
        {
            "home": os.path.expanduser("~"),
            "temp": tempfile.gettempdir(),
        }
    )

    return sublime.expand_variables(value, variables)


def find_project_root_for_view(view: sublime.View) -> Optional[str]:
    if (
        not (window := view.window())
        or not (filepath := view.file_name())
        or not (project_roots := window.folders())
        # ...
    ):
        return None

    if os.name == "nt":
        # fix drive cases
        filepath = str(Path(filepath).resolve())
        roots = map(str, (Path(root).resolve() for root in project_roots))
    else:
        roots = project_roots

    return next(filter(filepath.startswith, roots), None)


def lookup_syntax_for_cmd(cmd: str) -> Optional[str]:
    cmd = cmd.strip() + " "
    for prefix, syntax in SYNTAX_MAPPING.items():
        if cmd.startswith(f"{prefix} "):
            return syntax
    return None


def run_cli_command(
    cmd: Union[str, Sequence[str]],
    cwd: str = "",
    encoding: str = "utf-8",
    timeout_s: Optional[float] = None,
    shell: bool = False,
) -> Tuple[str, str, int]:
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
    cmd: Union[str, Sequence[str]],
    cwd: str = "",
    encoding: str = "utf-8",
    timeout_s: Optional[float] = None,
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
        if not cwd:
            if not (view := self.window.active_view()):
                sublime.error_message("No active view")
                return

            if project_root := find_project_root_for_view(view):
                cwd = project_root
            else:
                dirs: List[str] = []
                if filename := view.file_name():
                    dirs.append(os.path.dirname(filename))
                dirs.append("${home}")
                cwd = dirs[0]

        args: Dict[str, str] = expand_variables(self.window, {"cwd": cwd, "encoding": encoding})
        args["cwd"] = self.fix_cwd_unc(args["cwd"])

        self.cwd = args.get("cwd", "")
        self.encoding = args.get("encoding", "")
        self.shell = shell

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
        cmd: Optional[str] = None,
        cwd: str = "",
        encoding: str = "utf-8",
        shell: bool = False,
    ) -> None:
        if self.view.settings().get(self.VIEW_MARK):
            view = self.view

            settings = view.settings()
            cmd = settings.get("cli_runner/cmd")
            cwd = settings.get("cli_runner/cwd")
            encoding = settings.get("cli_runner/encoding")
            shell = settings.get("cli_runner/shell")
        else:
            if not (window := self.view.window()):
                return
            view = window.new_file()

        if not cmd:
            return

        try:
            output = get_cli_command_result_text(cmd, cwd=cwd, encoding=encoding, shell=shell)
        except:
            output = traceback.format_exc()

        if not (syntax := lookup_syntax_for_cmd(cmd)):
            first_line = output[:200].split("\n")[0]
            syntax = getattr(sublime.find_syntax_for_file("", first_line), "path", "scope:text.plain")

        settings = view.settings()
        settings.set(self.VIEW_MARK, True)
        settings.set("cli_runner/cmd", cmd)
        settings.set("cli_runner/cwd", cwd)
        settings.set("cli_runner/encoding", encoding)
        settings.set("cli_runner/shell", shell)

        view.set_scratch(True)
        view.set_name(f'({datetime.now().strftime("%Y%m%d%H%M%S")}) {cmd}')
        view.assign_syntax(syntax)

        view.replace(edit, sublime.Region(0, view.size()), "")
        view.insert(edit, 0, output)
        view.sel().clear()
        view.sel().add(0)
