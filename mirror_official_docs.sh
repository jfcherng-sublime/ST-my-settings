#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
NOW="$(date +'%Y/%m/%d %H:%M:%S')"
TODAY="$(date +'%Y%m%d')"

#---------#
# configs #
#---------#

HTTRACK="C:/_Tools/httrack_x64-noinst-3.49.2/httrack.exe"
USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36"
FOOTER="<div style='text-align:center; background:#ffff6e'>Snapshot on ${NOW}</div>"

function mirror() {
    output_dir="$1"
    start_url="$2"

    rm -rf "${output_dir}"

    pushd "${SCRIPT_DIR}" || exit

    echo "[⌛] Downloading..."

    "${HTTRACK}" \
        --path "${output_dir}" \
        --user-agent "${USER_AGENT}" \
        --referer "${start_url}" \
        --mirror "${start_url}" \
        --footer "${FOOTER}" \
        --stay-on-same-address \
        --display \
        --quiet \
        --max-rate=0 \
        +*.png +*.gif +*.jpg +*.jpeg +*.webp +*.css +*.js \
        -ad.doubleclick.net/*

    # redirect index page to website index
    index_file="${output_dir}/index.html"
    if [ -f "${index_file}" ]; then
        index_url=$(sed -zE 's/.* HREF="([^"]+)".*/\1/g' "${index_file}")
        echo "<meta http-equiv='refresh' content='0; url=${index_url}' />" \
            >"${output_dir}/index.html"
    fi

    cleanup "${output_dir}"

    popd || exit
}

function cleanup() {
    output_dir="$1"

    pushd "${output_dir}" || exit

    echo "[🧹] Clean up..."

    rm -rf \
        hts-cache/ \
        hts-log.txt \
        ./*.gif

    popd || exit
}

mirror \
    "${SCRIPT_DIR}/docs/ST_official_docs_${TODAY}" \
    "https://www.sublimetext.com/docs/index.html"

mirror \
    "${SCRIPT_DIR}/docs/SM_official_docs_${TODAY}" \
    "https://www.sublimemerge.com/docs/index.html"
