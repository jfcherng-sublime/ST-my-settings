#
# linter.py
# Markdown Linter for SublimeLinter, a code checking framework
# for Sublime Text 3
#
# Written by Jon LaBelle
# Copyright (c) 2018 Jon LaBelle
#
# License: MIT
#

"""This module exports the Markdownlint plugin class."""

from SublimeLinter.lint import NodeLinter, util
import sublime


class MarkdownLint(NodeLinter):
    """Provides an interface to markdownlint."""

    # there is a ":" in the filepath under Windows like C:\DIR\FILE
    if sublime.platform() == "windows":
        filepath_regex = r"[^:]+:[^:]+"
    else:
        filepath_regex = r"[^:]+"

    defaults = {
        'selector': 'text.html.markdown,'
                    'text.html.markdown.multimarkdown,'
                    'text.html.markdown.extended,'
                    'text.html.markdown.gfm'
    }
    cmd = ('markdownlint', '${args}', '${file}')
    regex = r'(?P<file>{0})[:]\s*(?P<line>\d+):\s+(?P<error>MD\d+)?[/]?(?P<message>.+)'.format(filepath_regex)
    multiline = False
    line_col_base = (1, 1)
    tempfile_suffix = '-'
    error_stream = util.STREAM_STDERR
    word_re = None
