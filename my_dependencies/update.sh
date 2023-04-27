#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

install_py() {
    export UV_PYTHON_DOWNLOADS=0
    export UV_BREAK_SYSTEM_PACKAGES=1
    export UV_SYSTEM_PYTHON=1

    cd "${SCRIPT_DIR}" || exit 1

    uv self update

    uv tool install --force ruff
    uv tool install --force ty
    uv tool upgrade --all

    # uv pip install --upgrade -r requirements.txt
}
install_py

install_js() {
    yarn_dir="$(yarn global dir)"
    if [[ -d ${yarn_dir} ]]; then
        cd "${yarn_dir}" || exit 1
        yarn upgrade
    fi
}
install_js
