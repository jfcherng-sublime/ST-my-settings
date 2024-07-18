from __future__ import annotations
import functools
from typing import Any, Callable, TypeVar, cast

import sublime
import sublime_plugin

_T_AnyCallable = TypeVar("_T_AnyCallable", bound=Callable)

PLUGIN_NAME = "jfcherng_dev_mode"

VIEW_STATUS_KEY_SHOW_SEL = "VIEW_STATUS_KEY_SHOW_SEL"
VIEW_STATUS_KEY_SHOW_WSVB_IDS = "VIEW_STATUS_KEY_SHOW_WSVB_IDS"


def plugin_loaded() -> None:
    """Executed when this plugin is loaded."""

    def _on_st_settings_changed() -> None:
        if not is_in_dev_mode():
            cleanup()

    st_settings = get_st_settings()
    st_settings.add_on_change(PLUGIN_NAME, _on_st_settings_changed)


def plugin_unloaded() -> None:
    """Executed when this plugin is unloaded."""
    cleanup()


def cleanup() -> None:
    for window in sublime.windows():
        for view in window.views(include_transient=True):
            view.erase_status(VIEW_STATUS_KEY_SHOW_SEL)
            view.erase_status(VIEW_STATUS_KEY_SHOW_WSVB_IDS)


def get_st_settings() -> sublime.Settings:
    return sublime.load_settings("Preferences.sublime-settings")


def is_in_dev_mode() -> bool:
    return get_st_settings().get("dev_mode", False)


def must_in_dev_mode(*, failed_return: Any = None) -> Callable[[_T_AnyCallable], _T_AnyCallable]:
    def _decorator(func: _T_AnyCallable) -> _T_AnyCallable:
        @functools.wraps(func)
        def _wrapped(*args, **kwargs) -> None:
            if not is_in_dev_mode():
                return failed_return
            return func(*args, **kwargs)

        return cast(_T_AnyCallable, _wrapped)

    return _decorator


class JfcherngDevModeListener(sublime_plugin.EventListener):
    @must_in_dev_mode()
    def on_selection_modified(self, view: sublime.View) -> None:
        self.show_sel(view)

    @must_in_dev_mode()
    def on_activated(self, view: sublime.View) -> None:
        self.show_wsvb_ids(view)

    def show_sel(self, view: sublime.View) -> None:
        region_reprs: list[str] = []
        for region in view.sel():
            region_reprs.append(f"{region.a}" if region.empty() else f"{region.a}-{region.b}")

        status_text = ",".join(region_reprs)
        view.set_status(VIEW_STATUS_KEY_SHOW_SEL, f"sel({status_text})")

    def show_wsvb_ids(self, view: sublime.View) -> None:
        window_id = window.id() if (window := view.window()) else "?"
        sheet_id = sheet.id() if (sheet := view.sheet()) else "?"
        view_id = view.id()
        buffer_id = view.buffer_id()

        view.set_status(VIEW_STATUS_KEY_SHOW_WSVB_IDS, f"w{window_id}/s{sheet_id}/v{view_id}/b{buffer_id}")
