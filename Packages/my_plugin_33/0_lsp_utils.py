import ctypes

try:
    from lsp_utils import node_runtime
    from lsp_utils.helpers import Optional, Tuple

    def get_glibc_version() -> Optional[Tuple[int, ...]]:
        try:
            libc = ctypes.CDLL("libc.so.6")
            gnu_get_libc_version = libc.gnu_get_libc_version
            gnu_get_libc_version.restype = ctypes.c_char_p
            version_str = gnu_get_libc_version().decode("utf-8")
            return tuple(map(int, version_str.split(".")))
        except Exception:
            return None

    glibc_ver = get_glibc_version()

    # @see https://github.com/electron/electron/releases
    # Note that although Electron v30 uses Node.js v20,
    # Electron v29 requires GLIBC_2.18 so it can't run on CentOS 7.9... 😢
    if not glibc_ver or glibc_ver >= (2, 18):
        node_runtime.ELECTRON_RUNTIME_VERSION = "30.0.0-alpha.1"
        node_runtime.ELECTRON_NODE_VERSION = "20.11.1"
    else:
        node_runtime.ELECTRON_RUNTIME_VERSION = "28.0.0"
        node_runtime.ELECTRON_NODE_VERSION = "18.18.2"
except Exception as e:
    print(__file__, e)
