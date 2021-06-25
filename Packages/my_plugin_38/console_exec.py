"""
Console Exec

Plugin for Sublime Text to execute a command and redirect its output
into a console window. This is based on the default exec command.
"""

from shlex import quote
from typing import Any, Dict, List, Optional
import os
import sublime
import sublime_plugin
import subprocess


class ConsoleExecCommand(sublime_plugin.WindowCommand):
    def run(
        self,
        cmd: List[str] = [],
        env: Dict[str, str] = {},
        path: str = "",
        shell: bool = False,
        win_console: Optional[List[str]] = None,
        unix_console: Optional[List[str]] = None,
    ) -> None:
        # Show message
        sublime.status_message("Running " + " ".join(cmd))

        # Get platform-specific command arguments
        if os.name == "nt":
            console = win_console or ["cmd.exe", "/c"]
            pause = ["pause"]
            console_cmd = console + cmd + ["&"] + pause
        else:
            console = unix_console or self.get_unix_console()
            pause = '; read -p "Press [Enter] to continue..."'
            escaped_cmd = " ".join([quote(x) for x in cmd])
            console_cmd = console + ["bash -c " + quote(escaped_cmd + pause)]

        # debug
        self.debug_print("reconstructed console_cmd is", console_cmd)

        # Default the to the current file's directory if no working directory
        # was provided
        window = sublime.active_window()
        view = window.active_view() if window else None
        file_name = view.file_name() if view else None
        cwd = os.path.dirname(file_name) if file_name else os.getcwd()

        # Get environment
        env = env.copy()
        if w := self.window.active_view():
            if user_env := w.settings().get("build_env"):
                env.update(user_env)

        # Get executing environment
        proc_env = os.environ.copy()
        proc_env.update(env)
        for key in proc_env:
            proc_env[key] = os.path.expandvars(proc_env[key])

        # Run in new console
        old_path = None
        try:
            # Set temporary PATH to locate executable in arg_list
            if path:
                old_path = os.environ["PATH"]
                os.environ["PATH"] = os.path.expandvars(path)
            subprocess.Popen(console_cmd, env=proc_env, cwd=cwd, shell=shell)
        finally:
            if old_path:
                os.environ["PATH"] = old_path

    def get_unix_console(self) -> List[str]:
        sessions = ["gnome-session", "ksmserver", "xfce4-session", "lxsession"]
        ps = 'ps -eo comm | grep -E "{0}"'.format("|".join(sessions))
        # get the first found session or an empty string
        session_found = os.popen(ps).read().split("\n")[0]
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
        # default
        else:
            console = ["xterm", "-e"]
        return console

    def debug_print(self, *arg: Any) -> None:
        print("Console Exec:", *arg)
