from __future__ import annotations

import ctypes
from typing import Callable, Iterable, TypeVar, overload

_T = TypeVar("_T")
_U = TypeVar("_U")


# from "more_itertools" package
@overload
def first_true(iterable: Iterable[_T], *, pred: Callable[[_T], object] | None = ...) -> _T | None: ...
@overload
def first_true(iterable: Iterable[_T], default: _U, pred: Callable[[_T], object] | None = ...) -> _T | _U: ...
def first_true(iterable, default=None, pred=None):
    return next(filter(pred, iterable), default)


def get_glibc_version() -> tuple[int, int] | None:
    try:
        libc = ctypes.CDLL("libc.so.6")
        gnu_get_libc_version = libc.gnu_get_libc_version
        gnu_get_libc_version.restype = ctypes.c_char_p
        version_str = gnu_get_libc_version().decode("utf-8")
        return tuple(map(int, version_str.split(".")))
    except Exception:
        return None


def revise_node_electron_version() -> None:
    from lsp_utils import node_runtime

    # To know the min glibc version requirement of "THE_BIN_FILE", run
    # $ objdump -T "THE_BIN_FILE" | command grep -Eo 'GLIBC_\S+' | sort -u

    # @see https://nodejs.org/en/download/prebuilt-binaries/
    node_min_reqs: tuple[tuple[tuple[int, int], str], ...] = (
        # ((min_glibc_version), "node_version"),
        ((2, 28), "22.10.0"),
        ((2, 25), "20.18.0"),
        ((2, 17), "17.9.1"),
    )
    # @see https://github.com/electron/electron/releases
    electron_min_reqs: tuple[tuple[tuple[int, int], str, str], ...] = (
        # ((min_glibc_version), "electron_version", "node_version"),
        ((2, 25), "33.0.1", "20.18.0"),
        ((2, 17), "28.3.3", "18.18.2"),
    )

    glibc_ver = get_glibc_version() or (99999, 0)

    if node_min_req := first_true(node_min_reqs, pred=lambda x: glibc_ver >= x[0]):
        node_runtime.NODE_RUNTIME_VERSION = node_min_req[1]
    else:
        print("[ERROR] glibc is too old for Node.js...")

    if electron_min_req := first_true(electron_min_reqs, pred=lambda x: glibc_ver >= x[0]):
        node_runtime.ELECTRON_RUNTIME_VERSION = electron_min_req[1]
        node_runtime.ELECTRON_NODE_VERSION = electron_min_req[2]
    else:
        print("[ERROR] glibc is too old for Electron...")


try:
    revise_node_electron_version()
except Exception as e:
    print(__file__, e)
