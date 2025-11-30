#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

ST_LSP_PACKAGE_PATH="${SCRIPT_DIR}/../Installed Packages/LSP.sublime-package"
INTERESTED_REF=${1:-main}
TMP_DIR="${SCRIPT_DIR}/tmp"

cleanup() {
    rm -rf "${TMP_DIR}"
}

if [ ! -f "${ST_LSP_PACKAGE_PATH}" ]; then
    echo "LSP package not found..."
    exit 1
fi

cleanup
mkdir -p "${TMP_DIR}"

git clone "https://github.com/sublimelsp/LSP.git" \
    --single-branch \
    --branch="${INTERESTED_REF}" \
    --depth=1 \
    "${TMP_DIR}/LSP"

if [[ $? != "0" ]]; then
    echo "Failed to clone LSP with ref: ${INTERESTED_REF}"
    exit 1
fi

# LSP stubs
TYPINGS_DIR=../typings/LSP
rm -rf "${TYPINGS_DIR}"
stubgen --include-private --include-docstrings "${TMP_DIR}/LSP" -o "${TYPINGS_DIR}"
pushd "${TYPINGS_DIR}" || exit
    rm -f test_* sublime.pyi sublime_plugin.pyi setup.pyi server.pyi release.pyi mdpopups.pyi
popd || exit
rm -rf .mypy_cache

pushd "${TMP_DIR}/LSP" || exit

# create package
git archive HEAD -o out.zip
7za x -aoa "${ST_LSP_PACKAGE_PATH}" "package-metadata.json"
7za a -aoa out.zip "package-metadata.json"

# replace ST's package
mv -f out.zip "${ST_LSP_PACKAGE_PATH}"

popd || exit

cleanup
