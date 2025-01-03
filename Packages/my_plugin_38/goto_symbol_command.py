"""
This command allows to navigate between symbols, which are listed in Ctrl+R.

Example keybindings:

```json
{ "keys": ["ctrl+shift+,"], "command": "goto_symbol", "args": {"step": -1, "cycle": false} },
{ "keys": ["ctrl+shift+."], "command": "goto_symbol", "args": {"step": 1, "cycle": false} },
```
"""

from __future__ import annotations

import bisect
from collections.abc import Sequence
from typing import Literal

import sublime
import sublime_plugin


class GotoSymbolCommand(sublime_plugin.TextCommand):
    def run(self, edit: sublime.Edit, *, step: Literal[-1, 1] = -1, cycle: bool = False) -> None:
        if not ((sel := self.view.sel()) and (sym_regions := self.view.symbol_regions())):
            return
        caret = sel[0].b

        found_idx = self._find_symbol_region_index(caret, sym_regions, step)
        if cycle:
            found_idx %= len(sym_regions)
        if not (0 <= found_idx < len(sym_regions)):
            return

        self._goto_symbol_region(sym_regions[found_idx])

    def _find_symbol_region_index(self, point: int, sym_regions: Sequence[sublime.SymbolRegion], step: int) -> int:
        """
        Finds a symbol region index.

        :param      point:        The point to find the symbol region index for.
        :param      sym_regions:  The symbol regions.
        :param      step:         The step value. `-1` for the previous symbol region, `1` for the next symbol region.

        :returns:   The symbol region index. Ranged from `-1` to `len(sym_regions)`.

        :raises     ValueError:  If `step` is invalid.
        """
        symbol_points = tuple(r.region.a for r in sym_regions)

        # prev
        if step == -1:
            return bisect.bisect_left(symbol_points, point) - 1
        # next
        if step == 1:
            return bisect.bisect_right(symbol_points, point)

        raise ValueError(f"Invalid step value: {step}")

    def _goto_symbol_region(self, sym_region: sublime.SymbolRegion) -> None:
        point = sym_region.region.a

        self.view.sel().clear()
        self.view.sel().add(point)
        self.view.show_at_center(point)
