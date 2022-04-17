#!/usr/bin/env bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"


#---------#
# configs #
#---------#

TEMP_DIR="${SCRIPT_DIR}/.Sublime-Official-Packages"
PKG_GITHUB_URL="https://github.com/sublimehq/Packages"
PKG_REMOTE_REPO="${PKG_GITHUB_URL}.git"

ST_INSTALL_DIRS=(
    # this script's dir and its parent (if you put this script in Data/)
    "${SCRIPT_DIR}"
    "${SCRIPT_DIR}/.."
    # Windows
    "C:/Program Files/Sublime Text"
    "C:/Program Files/Sublime Text 3"
    # Linux
    "/opt/sublime_text"
    "/opt/sublime_text_3"
    # Mac
    "/Applications/Sublime Text.app/Contents/MacOS"
    "/Applications/Sublime Text 3.app/Contents/MacOS"
)


#-----------#
# functions #
#-----------#

pushd() {
    # suppress messages from pushd, which is usually verbose
    command pushd "$@" > /dev/null
}

popd() {
    # suppress messages from popd, which is usually verbose
    command popd > /dev/null
}

##
## @brief      Clone the repo with ref
##
## @param      $1    Destination directory
## @param      $2    Repo URL
## @param      $3    Commit ref
##
## @return     The return code of last git operation
##
clone_repo_ref() {
    local repo_dir="$1"
    local repo_url="$2"
    local commit_ref="$3"

    rm -rf "${repo_dir}" && mkdir -p "${repo_dir}"
    pushd "${repo_dir}" || exit

    # @see https://stackoverflow.com/questions/3489173
    git init
    git remote add origin "${repo_url}"
    git fetch --depth=1 origin "${commit_ref}"
    git reset --hard FETCH_HEAD
    local retcode="$?"

    popd || exit

    return "${retcode}"
}


#-------#
# begin #
#-------#

pushd "${SCRIPT_DIR}" || exit

rm -rf "${TEMP_DIR}" && mkdir -p "${TEMP_DIR}"

pushd "${TEMP_DIR}" || exit


#-------------------------------------------#
# try to find the ST installation directory #
#-------------------------------------------#

paths_to_check=(
    "Packages/"
    "changelog.txt"
)

for st_install_dir in "${ST_INSTALL_DIRS[@]}"; do
    st_install_dir="${st_install_dir%/}"

    is_passed=1
    for path_to_check in "${paths_to_check[@]}"; do
        path_to_check="${st_install_dir}/${path_to_check}"

        # if the path under checking is a dir, it ends with a slash
        if [[ "${path_to_check}" =~ /$ ]]; then
            if [ ! -d "${path_to_check}" ]; then
                is_passed=0
                break
            fi
        else
            if [ ! -f "${path_to_check}" ]; then
                is_passed=0
                break
            fi
        fi
    done

    if [ "${is_passed}" = "1" ]; then
        st_install_dir="$(realpath "${st_install_dir}")"
        echo "[✔️] Found ST installation directory: ${st_install_dir}"
        break
    else
        st_install_dir=""
    fi
done

if [ "${st_install_dir}" = "" ]; then
    echo "[❌] Could not find ST installation directory..."
    exit 1
fi

st_pkgs_dir="${st_install_dir}/Packages"


#-------------------------#
# read option: commit_ref #
#-------------------------#

echo "[💡] You can use either branch, tag or even SHA as the ref."
echo "[💡] You can check out refs on '${PKG_GITHUB_URL}/commits'."
read -erp "[❓] Which ref you want to used (such as 'v4134', default = 'master'): " commit_ref

if [ "${commit_ref}" = "" ]; then
    commit_ref="master"
    echo "[⚠️] Use the default ref: ${commit_ref}"
fi


#-------------------------------#
# get the latest package source #
#-------------------------------#

repo_dir="${TEMP_DIR}/repo"
commit_sha=""

echo "[💬] Downloading repository..."

if clone_repo_ref "${repo_dir}" "${PKG_REMOTE_REPO}" "${commit_ref}"; then
    echo "[✔️] Download repository successfully!"
    commit_sha="$(git rev-parse HEAD)"
else
    echo "[❌] Fail to checkout ref: ${commit_ref}"
    exit 1
fi


#------------------#
# pack up packages #
#------------------#

packed_pkgs_dir="${TEMP_DIR}/packages"

mkdir -p "${packed_pkgs_dir}"

pushd "${repo_dir}" || exit

echo "[💬] Pack up packages (${commit_sha})..."

# traverse all packages in the repo
for dir in */; do
    pushd "${dir}" || exit

    pkg_name=${dir%/}

    echo "[📦] Packaging: ${pkg_name}"

    zip -9rq "${packed_pkgs_dir}/${pkg_name}.sublime-package" . -z <<END
Repository URL: ${PKG_REMOTE_REPO}
Commit SHA: ${commit_sha}
END

    popd || exit
done

popd || exit


#------------------#
# replace packages #
#------------------#

echo "[💬] Update ST packages to '${commit_ref}'..."
cp -rf "${packed_pkgs_dir}"/*.sublime-package "${st_pkgs_dir}"


#----------#
# clean up #
#----------#

popd || exit

echo "[🧹] Clean up..."
rm -rf "${TEMP_DIR}"


#-----#
# end #
#-----#

popd || exit
