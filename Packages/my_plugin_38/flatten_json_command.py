from __future__ import annotations

import json
from typing import Any

import sublime
import sublime_plugin


def flatten_dict(data: dict[Any, Any], *, sep: str = ".", prefix: str = "") -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in data.items():
        key = f"{prefix}{key}"
        if isinstance(value, dict):
            result.update(flatten_dict(value, sep=sep, prefix=f"{key}{sep}"))
        else:
            result[key] = value
    return result


class FlattenJsonCommand(sublime_plugin.TextCommand):
    def run(
        self,
        edit: sublime.Edit,
        *,
        ensure_ascii: bool = False,
        pretty: int | str | None = "\t",
        sep: str = ".",
    ) -> None:
        if len(sel := self.view.sel()) != 1:
            sublime.error_message("Please select only one region.")
            return

        if (region := sel[0]).empty():
            region = sublime.Region(0, self.view.size())

        text = self.view.substr(region)
        try:
            data = sublime.decode_value(text)
        except ValueError as e:
            sublime.error_message(f"Invalid JSON: {e}")
            return

        if not isinstance(data, dict):
            return

        flattened = flatten_dict(data, sep=sep)
        json_args = self._json_dump_args(pretty=pretty, ensure_ascii=ensure_ascii)
        self.view.replace(edit, region, json.dumps(flattened, **json_args))

    def _json_dump_args(
        self,
        *,
        ensure_ascii: bool = False,
        pretty: int | str | None = "\t",
    ) -> dict[str, Any]:
        args: dict[str, Any] = {
            "ensure_ascii": ensure_ascii,
            "indent": pretty,
        }
        if not pretty:
            args["separators"] = (",", ":")
        return args
