#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

(
    export UV_SYSTEM_PYTHON=1

    cd "${SCRIPT_DIR}" || exit 1

    uv self update
    uv pip install --upgrade -r requirements.txt
)

(
    yarn_dir="$(yarn global dir)"
    if [[ -d ${yarn_dir} ]]; then
        cd "${yarn_dir}" || exit 1
        yarn upgrade
    fi
)
