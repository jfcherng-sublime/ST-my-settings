#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
NOW="$(date +'%Y/%m/%d %H:%M:%S')"
TODAY="$(date +'%Y%m%d')"

#---------#
# configs #
#---------#

HTTRACK="C:/_Tools/httrack_x64-noinst-3.49.2/httrack.exe"
OUTPUT_DIR="${SCRIPT_DIR}/docs/ST_official_docs_${TODAY}"
START_URL="https://www.sublimetext.com/docs/index.html"

USER_AGENT="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36"
FOOTER="<div style='text-align:center; background:#ffff6e'>Snapshot on ${NOW}</div>"

#-------#
# begin #
#-------#

rm -rf "${OUTPUT_DIR}"

pushd "${SCRIPT_DIR}" || exit

echo "[⌛] Downloading..."

"${HTTRACK}" \
    --path "${OUTPUT_DIR}" \
    --user-agent "${USER_AGENT}" \
    --referer "${START_URL}" \
    --mirror "${START_URL}" \
    --footer "${FOOTER}" \
    --stay-on-same-address \
    --display \
    --quiet \
    --max-rate=0 \
    +*.png +*.gif +*.jpg +*.jpeg +*.webp +*.css +*.js \
    -ad.doubleclick.net/*

# redirect index page to website index
index_file="${OUTPUT_DIR}/index.html"
if [ -f "${index_file}" ]; then
    index_url=$(sed -zE 's/.* HREF="([^"]+)".*/\1/g' "${index_file}")
    echo "<meta http-equiv='refresh' content='0; url=${index_url}' />" \
        >"${OUTPUT_DIR}/index.html"
fi

#----------#
# clean up #
#----------#

pushd "${OUTPUT_DIR}" || exit

echo "[🧹] Clean up..."

rm -rf \
    hts-cache/ \
    hts-log.txt \
    ./*.gif

popd || exit

#-----#
# end #
#-----#

popd || exit
