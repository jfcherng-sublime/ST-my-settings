import importlib
from pathlib import Path

import sublime

try:
    # ------------------------------- #
    # override utils.find_root_file() #
    # ------------------------------- #

    utils = importlib.import_module("sublack.sublack").utils  # type: ignore

    find_root_file_original = utils.find_root_file

    def find_root_file_modified(view: sublime.View, filename: str):
        view_name = view.file_name()
        window = view.window()

        if not view_name or not window:
            return None

        folders = window.folders()
        if not folders:
            return None

        for folder in sorted(folders, key=len):
            if view_name.startswith(folder):
                path = Path(folder) / filename
                if path.exists():
                    return path

        return None

    utils.find_root_file = find_root_file_modified
except Exception as e:
    print(__file__, e)
