from __future__ import annotations

from lsp_utils.generic_client_handler import GenericClientHandler


class RuffLsp(GenericClientHandler):
    package_name = __package__

    @classmethod
    def binary_path(cls) -> str:
        return "ruff"

    @classmethod
    def get_binary_arguments(cls) -> list[str]:
        return ["server", "--preview"]


def plugin_loaded() -> None:
    RuffLsp.setup()


def plugin_unloaded() -> None:
    RuffLsp.cleanup()
