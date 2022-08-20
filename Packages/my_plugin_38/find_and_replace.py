import functools
import re
from dataclasses import dataclass
from typing import Optional

import sublime
import sublime_plugin


@dataclass
class FindReplacePair:
    find: Optional[str] = None
    replace: Optional[str] = None
    flags: Optional[str] = None


class FindAndReplaceCommand(sublime_plugin.WindowCommand):
    _input_captions = {
        "find": "Find (regex): ",
        "replace": "Replace (regex): ",
        "flags": "Flags (regex): ",
    }

    def run(
        self,
        find: Optional[str] = None,
        replace: Optional[str] = None,
        flags: Optional[str] = None,
    ) -> None:
        fr = FindReplacePair(find, replace, flags)
        self._ask_attr_and_replace(fr)

    def _ask_attr_and_replace(self, fr: FindReplacePair) -> None:
        for attr in self._input_captions.keys():
            if getattr(fr, attr, None) is None:
                return self._ask_user_input(attr, fr)
        self._do_replace(fr)

    def _ask_user_input(self, attr: str, fr: FindReplacePair) -> None:
        self.window.show_input_panel(
            self._input_captions[attr],
            "",
            on_done=functools.partial(self._user_input_done, attr=attr, fr=fr),
            on_change=None,
            on_cancel=None,
        )

    def _user_input_done(self, user_input: str, attr: str, fr: FindReplacePair) -> None:
        setattr(fr, attr, user_input)
        self._ask_attr_and_replace(fr)

    def _do_replace(self, fr: FindReplacePair) -> None:
        if not (v := self.window.active_view()):
            return

        v.run_command(
            "find_and_replace_worker",
            {
                "find": fr.find,
                "replace": fr.replace,
                "flags": fr.flags,
            },
        )


class FindAndReplaceWorkerCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, find: str, replace: str, flags: str = "") -> None:
        whole_region = sublime.Region(0, self.view.size())

        try:
            new_text = re.sub(
                find,
                replace,
                self.view.substr(whole_region),
                0,
                self._parse_regex_flags(flags),
            )
        except re.error as e:
            return sublime.error_message(str(e))

        sel = self.view.sel()
        seletions = list(sel)
        self.view.replace(edit, whole_region, new_text)
        sel.clear()
        sel.add_all(seletions)

    @staticmethod
    def _parse_regex_flags(flags: str) -> int:
        """
        Parse string regex flags into an int value.

        Valid flags are:
        `A (ASCII)`, `I (IGNORECASE)`, `L (LOCALE)`, `M (MULTILINE)`,
        `S (DOTALL)`, `X (VERBOSE)`, `U (UNICODE)`.

        @see https://docs.python.org/3.8/library/re.html#re.A
        """
        return functools.reduce(lambda c, el: c | el, (getattr(re, flag, 0) for flag in flags), 0)
