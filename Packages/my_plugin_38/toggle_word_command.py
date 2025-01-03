from __future__ import annotations

import re
from collections import UserList
from collections.abc import Iterable
from dataclasses import dataclass
from typing import TYPE_CHECKING

import sublime
import sublime_plugin


@dataclass
class WordInfo:
    word: str
    next_: WordInfo | None = None

    def __len__(self) -> int:
        return len(self.word)

    def __next__(self) -> WordInfo:
        if self.next_ is None:
            raise StopIteration
        return self.next_

    def __str__(self) -> str:
        return self.word


if TYPE_CHECKING:
    # requires py39+
    WordInfoUserList = UserList[WordInfo]
else:
    WordInfoUserList = UserList


class ToggleGroup(WordInfoUserList):
    def __init__(self, words: Iterable[str] | None = None) -> None:
        super().__init__()
        self.extend(words or [])

    def append(self, word: str) -> None:
        word_info = WordInfo(word)
        # make `self.data` circular
        if self.data:
            self.data[-1].next_ = word_info
        self.data.append(word_info)
        self.data[-1].next_ = self.data[0]

    def extend(self, words: Iterable[str]) -> None:
        for word in words:
            self.append(word)


class ToggleGroupCollection:
    def __init__(self, group_words: list[Iterable[str]]) -> None:
        self.groups = [ToggleGroup(words) for words in filter(None, group_words)]

        self.sorted_word_infos: list[WordInfo] = []
        self._sort_word_infos()

    def __bool__(self) -> bool:
        return bool(self.groups)

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
        string = view.substr(search_region)
        for word_info in self.sorted_word_infos:
            for m in re.finditer(re.escape(word_info.word), string, flags=re.IGNORECASE):
                m_a, m_b = m.span()
                if (found_region := sublime.Region(search_region.a + m_a, search_region.a + m_b)).contains(caret_pt):
                    return word_info, found_region
        return None

    def _sort_word_infos(self) -> None:
        """
        Extract all `word_info`s, whose `next_` has pointed to its next `word_info`.
        Sort them by their lengths, so that longer words are tried first later.
        """
        self.sorted_word_infos = sorted(
            (word_info for group in self.groups for word_info in group),
            key=len,
            reverse=True,
        )


class ToggleWordCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        preferences = sublime.load_settings("Preferences.sublime-settings")

        if not (group_collection := ToggleGroupCollection(preferences.get("toggle_word.groups", []))):
            return

        for region in reversed(self.view.sel()):
            region = sublime.Region(region.begin(), region.end())

            if (search_region := region).empty():
                search_radius = len(group_collection.longest_word)
                search_region = sublime.Region(region.a - search_radius, region.b + search_radius)

            self._toggle_word(
                self.view,
                edit,
                source_region=search_region,
                group_collection=group_collection,
                caret_pt=region.a,
            )

    def _toggle_word(
        self,
        view: sublime.View,
        edit: sublime.Edit,
        *,
        source_region: sublime.Region,
        group_collection: ToggleGroupCollection,
        caret_pt: int = -1,
    ) -> None:
        if not (find_result := group_collection.find(view, search_region=source_region, caret_pt=caret_pt)):
            return
        word_info, source_region = find_result

        next_word_info = next(word_info)
        source_text = view.substr(source_region)

        for set_case in (str, str.lower, str.upper, str.title):
            if source_text == set_case(word_info.word):
                view.replace(edit, source_region, set_case(next_word_info.word))
                return
