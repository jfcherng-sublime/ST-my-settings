from __future__ import annotations

import textwrap
from abc import ABC
from pathlib import Path
from typing import Literal

import sublime
import sublime_plugin

ST_USER_DIR = Path(sublime.packages_path()) / "User"


def reformat(template: str) -> str:
    return textwrap.dedent(template).lstrip()


class AbstractNewFileCommand(sublime_plugin.WindowCommand, ABC):
    save_path: Path = ST_USER_DIR / "untitled"
    template: str = ""
    template_type: Literal["snippet", "text"] = "text"

    @property
    def save_path_extension(self) -> str:
        """File extension, without a leading dot, of the save file."""
        return self.save_path.name.rpartition(".")[2]

    def run(self) -> None:
        self.save_path.parent.mkdir(parents=True, exist_ok=True)

        v = self.window.new_file()
        v.settings().update({
            "default_dir": str(self.save_path.parent),
            "default_extension": self.save_path_extension,
        })

        v.set_name(self.save_path.name)
        if syntax := sublime.find_syntax_for_file(self.save_path.name):
            v.assign_syntax(syntax)

        if self.template_type == "snippet":
            v.run_command("insert_snippet", {"contents": self.template})
        elif self.template_type == "text":
            v.run_command("append", {"characters": self.template})
        else:
            raise ValueError(f"Invalid template type: {self.template_type}")


class NewBuildSystemCommand(AbstractNewFileCommand):
    save_path: Path = ST_USER_DIR / "untitled.sublime-build"
    template = reformat("""
{
\t"shell_cmd": "${0:make}"
}
    """)
    template_type = "snippet"


class NewPluginCommand(AbstractNewFileCommand):
    save_path: Path = ST_USER_DIR / "untitled.py"
    template = reformat("""
from __future__ import annotations

import sublime
import sublime_plugin


class ExampleCommand(sublime_plugin.TextCommand):
\tdef run(self, edit: sublime.Edit) -> None:
\t\t${0:self.view.insert(edit, 0, "Hello, World!")}
    """)
    template_type = "snippet"


class NewSnippetCommand(AbstractNewFileCommand):
    save_path: Path = ST_USER_DIR / "untitled.sublime-snippet"
    template = reformat("""
<snippet>
\t<content><![CDATA[
Hello, \\${1:this} is a \\${2:snippet}.
]]></content>
\t<!-- Optional: Set a tabTrigger to define how to trigger the snippet -->
\t<!-- <tabTrigger>hello</tabTrigger> -->
\t<!-- Optional: Set a scope to limit where the snippet will trigger -->
\t<!-- <scope>source.python</scope> -->
</snippet>
    """)
    template_type = "snippet"


class NewSyntaxCommand(AbstractNewFileCommand):
    save_path: Path = ST_USER_DIR / "untitled.sublime-syntax"
    template = reformat(R"""
%YAML 1.2
---
# See http://www.sublimetext.com/docs/syntax.html
name: Example C
version: 2
file_extensions:
  - ec
scope: source.example-c
contexts:
  main:
    # Strings begin and end with quotes, and use backslashes as an escape
    # character
    - match: '"'
      scope: punctuation.definition.string.begin.example-c
      push: double_quoted_string

    # Comments begin with a '//' and finish at the end of the line
    - match: '//'
      scope: punctuation.definition.comment.example-c
      push: line_comment

    # Keywords are if, else for and while.
    # Note that blackslashes don't need to be escaped within single quoted
    # strings in YAML. When using single quoted strings, only single quotes
    # need to be escaped: this is done by using two single quotes next to each
    # other.
    - match: '\b(if|else|for|while)\b'
      scope: keyword.control.example-c

    # Numbers
    - match: '\b(-)?[0-9.]+\b'
      scope: constant.numeric.example-c

  double_quoted_string:
    - meta_scope: string.quoted.double.example-c
    - match: '\\.'
      scope: constant.character.escape.example-c
    - match: '"'
      scope: punctuation.definition.string.end.example-c
      pop: 1

  line_comment:
    - meta_scope: comment.line.example-c
    - match: $
      pop: 1
    """)
