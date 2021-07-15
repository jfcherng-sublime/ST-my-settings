#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

(
    pip install -U uv
    cd "${SCRIPT_DIR}" || exit 1
    uv pip install --system --upgrade -r requirements.txt
)

(
    yarn_dir="$(yarn global dir)"
    if [[ -d ${yarn_dir} ]]; then
        cd "${yarn_dir}" || exit 1
        yarn upgrade
    fi
)
