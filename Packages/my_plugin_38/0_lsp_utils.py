from __future__ import annotations

import ctypes


def get_glibc_version() -> tuple[int, ...] | None:
    try:
        libc = ctypes.CDLL("libc.so.6")
        gnu_get_libc_version = libc.gnu_get_libc_version
        gnu_get_libc_version.restype = ctypes.c_char_p
        version_str = gnu_get_libc_version().decode("utf-8")
        return tuple(map(int, version_str.split(".")))
    except Exception:
        return None


# To know the min glibc version requirement of "THE_BIN_FILE", run
# $ objdump -T "THE_BIN_FILE" | command grep -Eo 'GLIBC_\S+' | sort -u
glibc_ver = get_glibc_version()

try:
    from lsp_utils import node_runtime

    # @see https://nodejs.org/en/download/prebuilt-binaries/
    if not glibc_ver or glibc_ver >= (2, 25):
        node_runtime.NODE_RUNTIME_VERSION = "20.16.0"
    else:
        # 2.17 required
        node_runtime.NODE_RUNTIME_VERSION = "17.9.1"

    # @see https://github.com/electron/electron/releases
    if not glibc_ver or glibc_ver >= (2, 18):
        node_runtime.ELECTRON_RUNTIME_VERSION = "32.0.0"
        node_runtime.ELECTRON_NODE_VERSION = "20.16.0"
    else:
        # 2.17 required
        node_runtime.ELECTRON_RUNTIME_VERSION = "28.3.3"
        node_runtime.ELECTRON_NODE_VERSION = "18.18.2"
except Exception as e:
    print(__file__, e)
