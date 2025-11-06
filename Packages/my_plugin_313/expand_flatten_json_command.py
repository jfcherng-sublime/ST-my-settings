from __future__ import annotations

import json
from abc import ABC
from typing import Any

import sublime
import sublime_plugin


def flatten_dict(data: dict[Any, Any] | list[Any], *, sep: str = ".", prefix: str = "") -> dict[str, Any]:
    if isinstance(data, dict):
        kv_iterator = data.items()
    elif isinstance(data, list):
        kv_iterator = enumerate(data)
    else:
        raise TypeError(f"Expected dict or list, got {type(data).__name__}")

    result: dict[str, Any] = {}
    for key, value in kv_iterator:
        key = f"{prefix}{key}"
        if isinstance(value, (dict, list)):
            result.update(flatten_dict(value, sep=sep, prefix=f"{key}{sep}"))
        else:
            result[key] = value
    return result


def expand_json(data: dict[Any, Any] | list[Any], *, sep: str = ".") -> dict[Any, Any] | list[Any]:
    data_ = flatten_dict(data)  # ensure data structure

    result: dict[Any, Any] | list[Any] = {}
    for key, value in data_.items():
        if isinstance(value, (dict, list)):
            result[key] = expand_json(value, sep=sep)
        else:
            *sub_keys, last_sub_key = key.split(sep)
            current = result
            while sub_keys:
                if (sub_key := sub_keys.pop()) not in current:
                    current[sub_key] = {}
                current = current[sub_key]
            current[last_sub_key] = value
    return result


class BaseFlattenJsonCommand(sublime_plugin.TextCommand, ABC):
    def is_enabled(self) -> bool:
        return self.view.match_selector(0, "source.json | source.jsonc")

    def _ensure_region(self) -> sublime.Region | None:
        if len(sel := self.view.sel()) != 1:
            sublime.error_message("Please select only one region.")
            return

        if (region := sel[0]).empty():
            region = sublime.Region(0, self.view.size())
        return region

    def _ensure_data(self, region: sublime.Region) -> Any:
        text = self.view.substr(region)
        try:
            return sublime.decode_value(text)
        except ValueError:
            return None

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


class ExpandJsonCommand(BaseFlattenJsonCommand):
    def run(
        self,
        edit: sublime.Edit,
        *,
        ensure_ascii: bool = False,
        pretty: int | str | None = "\t",
        sep: str = ".",
    ) -> None:
        if not (region := self._ensure_region()):
            return

        if (data := self._ensure_data(region)) is None:
            return

        if not isinstance(data, (dict, list)):
            sublime.error_message(f"Expected dict or list, got {type(data).__name__}")
            return

        expanded = expand_json(data, sep=sep)
        json_args = self._json_dump_args(pretty=pretty, ensure_ascii=ensure_ascii)
        self.view.replace(edit, region, json.dumps(expanded, **json_args))


class FlattenJsonCommand(BaseFlattenJsonCommand):
    def run(
        self,
        edit: sublime.Edit,
        *,
        ensure_ascii: bool = False,
        pretty: int | str | None = "\t",
        sep: str = ".",
    ) -> None:
        if not (region := self._ensure_region()):
            return

        if (data := self._ensure_data(region)) is None:
            return

        if not isinstance(data, (dict, list)):
            sublime.error_message(f"Expected dict or list, got {type(data).__name__}")
            return

        flattened = flatten_dict(data, sep=sep)
        json_args = self._json_dump_args(pretty=pretty, ensure_ascii=ensure_ascii)
        self.view.replace(edit, region, json.dumps(flattened, **json_args))
