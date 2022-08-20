import importlib
import json
import os
from collections import OrderedDict

import sublime

template_variables = {
    "home": os.path.expanduser("~"),
    "st_cache_path": sublime.cache_path(),
    "st_executable_path": sublime.executable_path(),
    "st_installed_packages_path": sublime.installed_packages_path(),
    "st_packages_path": sublime.packages_path(),
}

templated_keys = {
    "php_cs_fixer_executable_path",
    "phpcbf_executable_path",
    "phpcs_executable_path",
    "phpcs_php_path",
    "phpcs_php_prefix_path",
    "phpmd_executable_path",
    "scheck_executable_path",
}

try:

    # -------------------- #
    # override Perf.load() #
    # -------------------- #

    Pref = importlib.import_module("Phpcs.phpcs").Pref  # type: ignore

    load_original = Pref.load

    def load_modified(self, *args, **kwargs) -> None:
        load_original(self, *args, **kwargs)

        for key in templated_keys:
            self.settings.set(key, sublime.expand_variables(self.settings.get(key), template_variables))

    Pref.load = load_modified

    # --------------------------- #
    # override Perf.get_setting() #
    # --------------------------- #

    get_setting_original = Pref.get_setting

    def get_setting_modified(self, key, *args, **kwargs):
        ret = get_setting_original(self, key, *args, **kwargs)

        if key == "php_cs_fixer_additional_args":
            rules = ret.get("--rules", "")
            if isinstance(rules, list):
                ret["--rules"] = json.dumps(OrderedDict(rules), ensure_ascii=False)

        return ret

    Pref.get_setting = get_setting_modified
except Exception as e:
    print(__file__, e)
