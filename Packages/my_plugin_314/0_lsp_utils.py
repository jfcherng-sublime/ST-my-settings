from __future__ import annotations

import ctypes
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


GLIBC_VER = get_glibc_version()


def revise_node_version_centos7() -> None:
    from lsp_utils import node_runtime
    from lsp_utils._node import node_constants, node_installer, node_manager, node_runner

    if not GLIBC_VER or sublime.arch() != "x64":
        return

    settings = sublime.load_settings("lsp_utils.sublime-settings")
    settings.set("local_use_electron", False)  # Node.js is forced

    node_min_reqs: tuple[tuple[GLIBC_VER_TUPLE, NODE_VER_STR, tuple[str, str] | None], ...] = (
        # (
        #     min_glibc_version,
        #     node_version,
        #     (
        #         filename_pattern,
        #         url_pattern,
        #     ),
        # ),
        (
            (2, 34),
            "24.15.0",
            (
                "node-v{version}-linux-x64.tar.gz",
                "https://github.com/sublimelsp/node-pointer-compression-builds/releases/download/v{version}/{filename}",
            ),
        ),
        (
            (2, 28),
            "24.15.0",
            (
                "node-v{version}-linux-x64.tar.xz",
                "https://nodejs.org/dist/v{version}/{filename}",
            ),
        ),
        (
            (2, 17),
            "22.22.2",
            (
                "node-v{version}-linux-x64-glibc-217.tar.xz",
                "https://unofficial-builds.nodejs.org/download/release/v{version}/{filename}",
            ),
        ),
    )

    if not (node_min_req := first_true(node_min_reqs, pred=lambda x: GLIBC_VER >= x[0])):
        print("[ERROR] glibc is too old for Node.js...")
        return

    _, node_version, (filename, url) = node_min_req
    filename = filename.format(version=node_version)
    url = url.format(version=node_version, filename=filename)

    # ------------------------------------------------------ #
    # legacy path: node_runtime (NpmClientHandler-based pkgs) #
    # ------------------------------------------------------ #

    node_runtime.NODE_DIST_URL = url
    node_runtime.NODE_RUNTIME_VERSION = node_version

    node_runtime.CUSTOM_NODE_DIST_URL = url
    node_runtime.CUSTOM_NODE_RUNTIME_VERSION = node_version

    class MyNodeRuntimeLocal(node_runtime.NodeRuntimeLocal):
        def __init__(
            self,
            base_dir: Path,
            node_version: str = node_version,
            node_dist_url: str = url,
        ) -> None:
            super().__init__(base_dir, node_version, node_dist_url)

    class MyNodeInstaller(node_runtime.NodeInstaller):
        def __init__(
            self,
            base_dir: Path,
            node_version: str = node_version,
            node_dist_url: str = url,
        ) -> None:
            super().__init__(base_dir, node_version, node_dist_url)

        def _node_archive(self) -> tuple[str, str]:
            return (filename, url)

    node_runtime.NodeRuntimeLocal = MyNodeRuntimeLocal
    node_runtime.NodeInstaller = MyNodeInstaller

    # ------------------------------------------------- #
    # new path: _node.* (NodeManager-based pkgs)        #
    # ------------------------------------------------- #

    node_constants.NODE_DIST_URL = url
    node_constants.NODE_RUNTIME_VERSION = node_version
    node_installer.NODE_DIST_URL = url

    class MyNodeManagerInstaller(node_installer.NodeInstaller):
        def __init__(self, base_dir: Path, node_version: str = node_version) -> None:
            super().__init__(base_dir, node_version)

        def _node_archive(self) -> tuple[str, str]:
            return (filename, url)

    class MyNodeRunnerLocal(node_runner.NodeRunnerLocal):
        # upstream's default node_version was baked in from node_constants at import
        # time and NodeManager calls NodeRunnerLocal(runtime_dir) with no version,
        # so the default itself must be replaced
        def __init__(self, base_dir: Path, node_version: str = node_version) -> None:
            super().__init__(base_dir, node_version)

    node_installer.NodeInstaller = MyNodeManagerInstaller
    node_runner.NodeInstaller = MyNodeManagerInstaller  # used by NodeRunnerLocal.install_node()
    node_runner.NodeRunnerLocal = MyNodeRunnerLocal
    node_manager.NodeRunnerLocal = MyNodeRunnerLocal  # used by NodeManager._resolve_node_runtime()


try:
    revise_node_version_centos7()
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
