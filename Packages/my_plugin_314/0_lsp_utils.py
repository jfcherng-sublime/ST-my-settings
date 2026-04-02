from __future__ import annotations

import ctypes
from functools import partial
from pathlib import Path

import sublime
from more_itertools import first_true

type ELECTRON_VER_STR = str
type GLIBC_VER_TUPLE = tuple[int, int]
type NODE_VER_STR = str


def get_glibc_version() -> GLIBC_VER_TUPLE | None:
    try:
        libc = ctypes.CDLL("libc.so.6")
        gnu_get_libc_version = libc.gnu_get_libc_version
        gnu_get_libc_version.restype = ctypes.c_char_p
        version_str = gnu_get_libc_version().decode("utf-8")
        return tuple(map(int, version_str.split(".")))  # type: ignore
    except Exception:
        return None


GLIBC_VER: GLIBC_VER_TUPLE = get_glibc_version() or (99999, 0)


def is_centos7_like() -> bool:
    return GLIBC_VER == (2, 17) and sublime.arch() == "x64"


def revise_node_electron_version_centos7() -> None:
    from lsp_utils import node_runtime

    settings = sublime.load_settings("lsp_utils.sublime-settings")
    settings.set("local_use_electron", False)  # Node.js is forced

    node_runtime_version = "22.22.2"
    node_runtime.NODE_RUNTIME_VERSION = node_runtime_version

    # -------------------- #
    # fix NodeRuntimeLocal #
    # -------------------- #

    class MyNodeRuntimeLocal(node_runtime.NodeRuntimeLocal):
        def __init__(self, base_dir: Path, node_version: str = node_runtime_version) -> None:
            super().__init__(base_dir, node_version)

    node_runtime.NodeRuntimeLocal = MyNodeRuntimeLocal

    # ----------------- #
    # fix NodeInstaller #
    # ----------------- #

    class MyNodeInstaller(node_runtime.NodeInstaller):
        def __init__(self, base_dir: Path, node_version: str = node_runtime_version) -> None:
            super().__init__(base_dir, node_version)

        def _node_archive(self) -> tuple[str, str]:
            return (
                f"node-v{self._node_version}-linux-x64-glibc-217.tar.xz",
                f"https://unofficial-builds.nodejs.org/download/release/v{self._node_version}/node-v{self._node_version}-linux-x64-glibc-217.tar.xz",
            )

    node_runtime.NodeInstaller = MyNodeInstaller


def revise_node_electron_version() -> None:
    from lsp_utils import node_runtime

    # To know the min glibc version requirement of "THE_BIN_FILE", run
    # $ objdump -T "THE_BIN_FILE" | command grep -Eo 'GLIBC_[0-9.]+' | sort -uV | tail -1

    # @see https://nodejs.org/download/release/
    node_min_reqs: tuple[tuple[GLIBC_VER_TUPLE, NODE_VER_STR], ...] = (
        # ((min_glibc_version), "node_version"),
        ((2, 28), "24.15.0"),
        ((2, 17), "17.9.1"),
    )
    # @see https://github.com/electron/electron/releases
    electron_min_reqs: tuple[tuple[GLIBC_VER_TUPLE, ELECTRON_VER_STR, NODE_VER_STR], ...] = (
        # ((min_glibc_version), "electron_version", "node_version"),
        ((2, 25), "42.0.0-alpha.1", "24.14.0"),
        ((2, 18), "29.4.6", "20.9.0"),
        ((2, 17), "28.3.3", "18.18.2"),
    )

    if node_min_req := first_true(node_min_reqs, pred=lambda x: GLIBC_VER >= x[0]):
        node_runtime.NODE_RUNTIME_VERSION = node_min_req[1]
    else:
        print("[ERROR] glibc is too old for Node.js...")

    if electron_min_req := first_true(electron_min_reqs, pred=lambda x: GLIBC_VER >= x[0]):
        node_runtime.ELECTRON_RUNTIME_VERSION = electron_min_req[1]
        node_runtime.ELECTRON_NODE_VERSION = electron_min_req[2]
    else:
        print("[ERROR] glibc is too old for Electron...")


try:
    if is_centos7_like():
        print("[INFO] This machine is like old CentOS 7")
        revise_node_electron_version_centos7()
    else:
        revise_node_electron_version()
except Exception as e:
    print(__file__, e)

# Shell script for finding min glibc version
"""
#!/usr/bin/env bash

find_glibc() {
    local file=$1

    echo "[INFO] The min GLIBC version is..."
    objdump -T "${file}" | command grep -Eo 'GLIBC_[0-9.]+' | sort -uV | tail -1
}

find_glibc_node() {
    local v=$1

    wget "https://nodejs.org/dist/v${v}/node-v${v}-linux-x64.tar.xz"
    tar axf "node-v${v}-linux-x64.tar.xz"
    find_glibc "node-v${v}-linux-x64/bin/node"
}

find_glibc_electron() {
    local v=$1

    wget "https://github.com/electron/electron/releases/download/v${v}/electron-v${v}-linux-x64.zip"
    unzip -oq "electron-v${v}-linux-x64.zip" -d "electron-v${v}-linux-x64"
    find_glibc "electron-v${v}-linux-x64/electron"
}
"""
