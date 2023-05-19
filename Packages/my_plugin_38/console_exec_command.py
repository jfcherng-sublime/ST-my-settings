from __future__ import annotations

import os
import shlex
import subprocess
import tempfile
import textwrap
from typing import Any

import sublime
import sublime_plugin

PLUGIN_NAME = os.path.basename(__file__)


def reformat(s: str) -> str:
    return textwrap.dedent(s).lstrip()


class ConsoleExecCommand(sublime_plugin.WindowCommand):
    """
    Execute a command and redirect its output into a console window.
    This is based on the default exec command.
    """

    def run(
        self,
        cmd: list[str] = [],
        env: dict[str, str] = {},
        path: str = "",
        shell: bool = False,
        working_dir: str | None = None,
        win_console: list[str] | None = None,
        unix_console: list[str] | None = None,
        **kwargs: Any,
    ) -> None:
        if not (view := self.window.active_view()):
            return

        sublime.status_message(f"Running {' '.join(cmd)}")

        if os.name == "nt":
            console = win_console or ["cmd.exe", "/c"]
            pause = ["pause"]
            console_cmd = console + cmd + ["&"] + pause
        else:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", prefix="st-exec-", delete=False) as f:
                f.write(self.generate_linux_script(cmd))
                os.chmod(f.name, 0o777)
            console = unix_console or self.get_unix_console()
            console_cmd = console + [f.name]

        self.debug_print(f"reconstructed {console_cmd = }")

        # default to the current file's directory if no working directory was provided
        if working_dir:
            cwd = working_dir
        else:
            cwd = os.path.dirname(filename) if (filename := view.file_name()) else os.getcwd()

        self.debug_print(f"{cwd = }")

        # get environment
        if user_env := view.settings().get("build_env"):
            env.update(user_env)

        # get executing environment
        proc_env = {**os.environ, **env}
        for key in proc_env:
            proc_env[key] = os.path.expandvars(proc_env[key])

        # run in new console
        old_path: str | None = None
        try:
            # set temporary PATH to locate executable
            if path:
                old_path = os.environ["PATH"]
                os.environ["PATH"] = os.path.expandvars(path)
            subprocess.Popen(console_cmd, env=proc_env, cwd=cwd, shell=shell)
        finally:
            if old_path:
                os.environ["PATH"] = old_path

    def get_unix_console(self) -> list[str]:
        sessions = ["gnome-session", "ksmserver", "xfce4-session", "lxqt-session", "lxsession"]
        ps = f'ps -eo comm | grep -E "{"|".join(sessions)}"'
        # get the first found session or an empty string
        session_found = os.popen(ps).read().partition("\n")[0]
        # Gnome
        if session_found == "gnome-session":
            console = ["gnome-terminal", "-e"]
        # XDE
        elif session_found == "xfce4-session":
            console = ["terminal", "-e"]
        # KDE
        elif session_found == "ksmserver":
            console = ["konsole", "-e"]
        # LXDE
        elif session_found == "lxsession":
            console = ["lxterminal", "-e"]
        # LXQT
        elif session_found == "lxqt-session":
            console = ["qterminal", "-e"]
        # default
        else:
            console = ["xterm", "-e"]
        return console

    @staticmethod
    def generate_linux_script(cmd: list[str]) -> str:
        escaped_cmd = " ".join(map(shlex.quote, cmd))
        return reformat(f"""
            #!/usr/bin/env bash
            {escaped_cmd}
            echo
            echo "Press any key to continue..."
            read -n1
        """)

    def debug_print(self, *arg: Any, **kwargs: Any) -> None:
        print(f"[{PLUGIN_NAME}]", *arg, **kwargs)
