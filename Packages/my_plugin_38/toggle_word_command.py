from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, Iterator, List, Optional, Tuple

import sublime
import sublime_plugin


@dataclass
class WordInfo:
    word: str
    next_: WordInfo = field(init=False)


class ToggleGroup:
    def __init__(self, words: Optional[Iterable[str]] = None) -> None:
        self._word_infos: List[WordInfo] = []
        self.extend(words or [])

    def __iter__(self) -> Iterator[WordInfo]:
        return iter(self._word_infos)

    def __len__(self) -> int:
        return len(self._word_infos)

    def append(self, word: str) -> None:
        word_info = WordInfo(word)
        # make `self.word_infos` circular
        if self._word_infos:
            self._word_infos[-1].next_ = word_info
        self._word_infos.append(word_info)
        self._word_infos[-1].next_ = self._word_infos[0]

    def extend(self, words: Iterable[str]) -> None:
        for word in words:
            self.append(word)


class ToggleGroups:
    def __init__(self, group_words: List[Iterable[str]]) -> None:
        groups = [ToggleGroup(words) for words in filter(None, group_words)]

        # sort words by their length, so that longer words are tried first
        self._word_infos: List[WordInfo] = sorted(
            (word_info for group in groups for word_info in group),
            key=lambda word_info: len(word_info.word),
            reverse=True,
        )

    def is_empty(self) -> bool:
        return not self._word_infos

    @property
    def longest_word_length(self) -> int:
        return len(self._word_infos[0].word) if self._word_infos else 0

    def find(
        self,
        view: sublime.View,
        *,
        search_region: sublime.Region,
        caret_pt: int,
    ) -> Optional[Tuple[WordInfo, sublime.Region]]:
        string = view.substr(search_region)
        for word_info in self._word_infos:
            for m in re.finditer(re.escape(word_info.word), string, flags=re.IGNORECASE):
                m_a, m_b = m.span()
                if (found_region := sublime.Region(search_region.a + m_a, search_region.a + m_b)).contains(caret_pt):
                    return word_info, found_region
        return None


class ToggleWordCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        preferences = sublime.load_settings("Preferences.sublime-settings")

        if (toggle_groups := ToggleGroups(preferences.get("toggle_word.groups", []))).is_empty():
            return

        for region in self.view.sel():
            region = sublime.Region(region.begin(), region.end())

            if (search_region := region).empty():
                search_radius = toggle_groups.longest_word_length
                search_region = sublime.Region(region.a - search_radius, region.b + search_radius)

            self._toggle_word(
                self.view,
                edit,
                source_region=search_region,
                toggle_groups=toggle_groups,
                caret_pt=region.a,
            )

    def _toggle_word(
        self,
        view: sublime.View,
        edit: sublime.Edit,
        *,
        source_region: sublime.Region,
        toggle_groups: ToggleGroups,
        caret_pt: int = -1,
    ) -> None:
        if not (find_result := toggle_groups.find(view, search_region=source_region, caret_pt=caret_pt)):
            return

        word_info, source_region = find_result
        next_word_info = word_info.next_
        source_text = view.substr(source_region)

        for set_case in (str, str.lower, str.upper, str.title):
            if source_text == set_case(word_info.word):
                view.replace(edit, source_region, set_case(next_word_info.word))
                return
