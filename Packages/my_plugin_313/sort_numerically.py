from __future__ import annotations

from collections.abc import Generator, Iterable
from itertools import dropwhile

import sublime
import sublime_plugin
from more_itertools import first
from natsort import realsorted


def drop_falsy[T](iterable: Iterable[T]) -> Generator[T]:
    yield from filter(None, iterable)


def drop_leading_empty_regions(regions: Iterable[sublime.Region]) -> Generator[sublime.Region]:
    yield from dropwhile(lambda r: r.empty(), regions)


def merge_contiguous_regions(regions: Iterable[sublime.Region]) -> Generator[sublime.Region]:
    if not regions:
        return

    region_it = iter(regions)
    try:
        current_region = next(region_it)
    except StopIteration:
        return

    for region in region_it:
        if current_region.end() >= region.begin():
            current_region = sublime.Region(current_region.begin(), max(current_region.end(), region.end()))
        else:
            yield current_region
            current_region = region
    yield current_region


def expand_region_to_full_lines(view: sublime.View, region: sublime.Region) -> sublime.Region:
    return sublime.Region(view.line(region.begin()).a, view.line(region.end()).b)


def strip_empty_lines(view: sublime.View, region: sublime.Region) -> sublime.Region | None:
    line_regions = view.lines(region)
    try:
        region_begin = first(drop_leading_empty_regions(line_regions)).begin()
        region_end = first(drop_leading_empty_regions(reversed(line_regions))).end()
    except ValueError:
        return None
    return sublime.Region(region_begin, region_end)


class SortNumericallyCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit) -> None:
        regions = list(self.view.sel())

        # selection is empty, use the entire buffer
        if len(regions) == 1 and regions[0].empty():
            regions = [sublime.Region(0, self.view.size())]
        else:
            regions = list(
                merge_contiguous_regions(expand_region_to_full_lines(self.view, region) for region in self.view.sel())
            )

        # remove leading/trailing empty lines and merge contiguous regions
        # this seems to be how ST's built-in "sort" command works
        regions = list(drop_falsy(map(lambda r: strip_empty_lines(self.view, r), regions)))

        if not regions:
            return

        for region in reversed(regions):
            input_lines = self.view.substr(region).split("\n")
            sorted_lines = realsorted(input_lines)
            self.view.replace(edit, region, "\n".join(sorted_lines))
        self.view.sel().clear()
        self.view.sel().add_all(regions)
