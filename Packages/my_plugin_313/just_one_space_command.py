from __future__ import annotations

from collections.abc import Generator, Iterable

import sublime
import sublime_plugin


class JustOneSpaceCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, *, space_chars: str = " ", replacement: str = " ") -> None:
        sel = self.view.sel()

        space_regions = list(self.extend_space_regions(regions=sel, space_chars=space_chars))

        sel.clear()
        for region in reversed(space_regions):
            if region:
                self.view.replace(edit, region, replacement)
            sel.add(region.a)

    def extend_space_regions(
        self,
        *,
        regions: Iterable[sublime.Region],
        space_chars: str,
    ) -> Generator[sublime.Region, None, None]:
        def extend_space_region(region: sublime.Region) -> sublime.Region:
            view_size = self.view.size()
            pt_l = pt_r = region.b  # the visual caret position
            while pt_l > 0 and self.view.substr(pt_l - 1) in space_chars:
                pt_l -= 1
            while pt_r < view_size and self.view.substr(pt_r) in space_chars:
                pt_r += 1
            return sublime.Region(pt_l, pt_r)

        yield from self.merge_overlapped_regions(sorted(map(extend_space_region, regions)))

    @staticmethod
    def merge_overlapped_regions(regions: Iterable[sublime.Region]) -> Generator[sublime.Region, None, None]:
        # assume `regions` is sorted and regions in it are normalized (.a <= .b)
        prev_ = next_ = None

        for region in regions:
            next_ = region

            if prev_ is not None:
                if prev_.intersects(next_):
                    prev_ = sublime.Region(prev_.a, next_.b)
                    continue
                yield prev_

            prev_ = next_

        if prev_ is not None:
            yield prev_
