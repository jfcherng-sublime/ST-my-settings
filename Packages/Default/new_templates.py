from __future__ import annotations

import os
import sublime
import sublime_plugin
import textwrap

ST_USER_DIR = os.path.join(sublime.packages_path(), "User")


def reformat(template: str) -> str:
    return textwrap.dedent(template).lstrip()


class NewBuildSystemCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        v = self.window.new_file()
        v.settings().set("default_dir", ST_USER_DIR)
        v.assign_syntax("Packages/JavaScript/JSON.sublime-syntax")
        v.set_name("untitled.sublime-build")

        template = reformat(
            """
            {
            \t"shell_cmd": "${0:make}"
            }
            """
        )
        v.run_command("insert_snippet", {"contents": template})


class NewPluginCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        v = self.window.new_file()
        v.settings().set("default_dir", ST_USER_DIR)
        v.assign_syntax("Packages/Python/Python.sublime-syntax")

        template = reformat(
            """
            import sublime
            import sublime_plugin


            class ExampleCommand(sublime_plugin.TextCommand):
            \tdef run(self, edit: sublime.Edit) -> None:
            \t\t$0self.view.insert(edit, 0, "Hello, World!")
            """
        )
        v.run_command("insert_snippet", {"contents": template})


class NewSnippetCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        v = self.window.new_file()
        v.settings().set("default_dir", ST_USER_DIR)
        v.settings().set("default_extension", "sublime-snippet")
        v.assign_syntax("Packages/XML/XML.sublime-syntax")

        template = reformat(
            """
            <snippet>
            \t<content><![CDATA[
            Hello, \\${1:this} is a \\${2:snippet}.
            ]]></content>
            \t<!-- Optional: Set a tabTrigger to define how to trigger the snippet -->
            \t<!-- <tabTrigger>hello</tabTrigger> -->
            \t<!-- Optional: Set a scope to limit where the snippet will trigger -->
            \t<!-- <scope>source.python</scope> -->
            </snippet>
            """
        )
        v.run_command("insert_snippet", {"contents": template})


class NewSyntaxCommand(sublime_plugin.WindowCommand):
    def run(self) -> None:
        v = self.window.new_file()
        v.settings().set("default_dir", ST_USER_DIR)
        v.settings().set("default_extension", "sublime-syntax")
        v.assign_syntax("Packages/YAML/YAML.sublime-syntax")

        template = reformat(
            R"""
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
            """
        )

        v.run_command("append", {"characters": template})
