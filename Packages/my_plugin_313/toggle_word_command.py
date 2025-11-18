"""
This plugin provides command: toggle_word

"toggle_word" command toggles words based on user-defined groups in the settings.

Example setup in "Preferences.sublime-settings".

```js
{
    "toggle_word.groups": [
        ["true", "false"],
        ["yes", "no"],
    ],
}
```
"""

from __future__ import annotations

import re
from collections import UserList
from collections.abc import Iterable
from dataclasses import dataclass
from typing import Self

import sublime
import sublime_plugin


def get_toggle_word_groups() -> list[list[str]]:
    preferences = sublime.load_settings("Preferences.sublime-settings")
    return preferences.get("toggle_word.groups") or []


@dataclass
class WordInfo:
    word: str
    next_: Self | None = None

    def __len__(self) -> int:
        return len(self.word)

    def __next__(self) -> Self:
        if self.next_ is None:
            raise StopIteration
        return self.next_

    def __str__(self) -> str:
        return self.word


class ToggleGroup(UserList[WordInfo]):
    def __init__(self, words: Iterable[str] | None = None) -> None:
        super().__init__()

        self.extend(words or [])

    def append(self, word: str) -> None:
        self.extend((word,))

    def extend(self, words: Iterable[str]) -> None:
        for word in words:
            word_info = WordInfo(word)
            if self.data:
                self.data[-1].next_ = word_info
            self.data.append(word_info)
        if self.data:
            self.data[-1].next_ = self.data[0]


class ToggleGroupCollection(UserList[ToggleGroup]):
    def __init__(self, groups_words: list[Iterable[str]]) -> None:
        super().__init__()

        self.data[:] = filter(None, map(ToggleGroup, groups_words))
        self.sorted_word_infos: list[WordInfo] = []
        """Sorted by length, so that longer words will be tried first later."""

        self._sort_word_infos()

    @property
    def longest_word(self) -> str:
        return self.sorted_word_infos[0].word if self.sorted_word_infos else ""

    def find(
        self,
        view: sublime.View,
        *,
        search_region: sublime.Region,
        caret_pt: int,
    ) -> tuple[WordInfo, sublime.Region] | None:
        search_offset = search_region.begin()
        string = view.substr(search_region)
        for word_info in self.sorted_word_infos:
            for m in re.finditer(re.escape(word_info.word), string, flags=re.IGNORECASE):
                found_region = sublime.Region(search_offset + m.start(), search_offset + m.end())
                if found_region.contains(caret_pt):
                    return word_info, found_region
        return None

    def _sort_word_infos(self) -> None:
        self.sorted_word_infos = sorted(
            (word_info for group in self.data for word_info in group),
            key=len,
            reverse=True,
        )


class ToggleWordCommand(sublime_plugin.TextCommand):
    CASE_CONVERTERS = (str, str.lower, str.upper, str.title, str.swapcase)

    def run(self, edit: sublime.Edit) -> None:
        if not (group_collection := ToggleGroupCollection(get_toggle_word_groups())):
            return

        search_radius = len(group_collection.longest_word)
        for region in reversed(self.view.sel()):
            if (search_region := region).empty():
                search_region = sublime.Region(region.b - search_radius, region.b + search_radius)
            self._toggle_word(
                self.view,
                edit,
                search_region=search_region,
                group_collection=group_collection,
                caret_pt=region.b,
            )

    def _toggle_word(
        self,
        view: sublime.View,
        edit: sublime.Edit,
        *,
        search_region: sublime.Region,
        group_collection: ToggleGroupCollection,
        caret_pt: int = -1,
    ) -> None:
        if not (find_result := group_collection.find(view, search_region=search_region, caret_pt=caret_pt)):
            return
        word_info, found_region = find_result

        word_info_next = next(word_info)
        source_text = view.substr(found_region)

        for set_case in self.CASE_CONVERTERS:
            if source_text == set_case(word_info.word):
                view.replace(edit, found_region, set_case(word_info_next.word))
                return
        print(f"[ToggleWord][ERROR] No matching case converter found for source text: {source_text}")
