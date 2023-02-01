#!/usr/bin/env bash

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"

# ------ #
# colors #
# ------ #

if [[ ${FORCE_COLOR} == "0" ]]; then
    C_RESET=""
    H_DEBUG="[DEBUG]"
    H_INFO="[INFO]"
    H_WARNING="[WARNING]"
    H_ERROR="[ERROR]"
else
    C_RESET="\e[0m"
    H_DEBUG="[\e[0;30;47mDEBUG${C_RESET}]"
    H_INFO="[\e[0;37;44mINFO${C_RESET}]"
    H_WARNING="[\e[0;30;43mWARNING${C_RESET}]"
    H_ERROR="[\e[0;37;41mERROR${C_RESET}]"
fi

#---------#
# configs #
#---------#

TEMP_DIR="${SCRIPT_DIR}/.Sublime-Official-Packages"
PKG_GITHUB_URL="https://github.com/sublimehq/Packages"
PKG_REMOTE_REPO="${PKG_GITHUB_URL}.git"

ST_INSTALL_DIRS=(
    # this script's dir and its parents (in case you put this script in "Data/" or deeper)
    "${SCRIPT_DIR}"
    "${SCRIPT_DIR}/.."
    "${SCRIPT_DIR}/../.."
    # Windows
    "C:/Program Files/Sublime Text"
    "C:/Program Files/Sublime Text 3"
    # Linux
    "${HOME}/opt/sublime_text"
    "${HOME}/opt/sublime_text_3"
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
    command pushd "$@" >/dev/null
}

popd() {
    # suppress messages from popd, which is usually verbose
    command popd >/dev/null
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
    git cherry-pick -n FETCH_HEAD
    local retcode="$?"

    popd || exit

    return "${retcode}"
}

#-------#
# begin #
#-------#

rm -rf "${TEMP_DIR}" && mkdir -p "${TEMP_DIR}"

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
        if [[ ${path_to_check} =~ /$ ]]; then
            if [[ ! -d ${path_to_check} ]]; then
                is_passed=0
                break
            fi
        else
            if [[ ! -f ${path_to_check} ]]; then
                is_passed=0
                break
            fi
        fi
    done

    if [[ ${is_passed} == "1" ]]; then
        st_install_dir="$(realpath "${st_install_dir}")"
        echo -e "${H_INFO} ✔️ Found ST installation directory: ${st_install_dir}"
        break
    else
        st_install_dir=""
    fi
done

if [[ ${st_install_dir} == "" ]]; then
    echo -e "${H_ERROR} ❌ Could not find ST installation directory..."
    exit 1
fi

st_pkgs_dir="${st_install_dir}/Packages"

#-------------------------#
# read option: commit_ref #
#-------------------------#

echo -e "${H_INFO} 💡 You can use either branch, tag or even SHA as the ref."
echo -e "${H_INFO} 💡 You can check out refs on \"${PKG_GITHUB_URL}/commits\"."
read -rp "$(echo -e "${H_INFO} ❓ Which ref you want to used (such as 'v4134', default = 'master'): ")" commit_ref

if [[ ${commit_ref} == "" ]]; then
    commit_ref="master"
    echo -e "${H_WARNING} ⚠️ Use the default ref: ${commit_ref}"
fi

#-------------------------------#
# get the latest package source #
#-------------------------------#

repo_dir="${TEMP_DIR}/repo"
commit_sha=""

echo -e "${H_INFO} 💬 Downloading repository..."

if clone_repo_ref "${repo_dir}" "${PKG_REMOTE_REPO}" "${commit_ref}"; then
    echo -e "${H_INFO} ✔️ Download repository successfully!"
    commit_sha="$(git rev-parse HEAD)"
else
    echo -e "${H_ERROR} ❌ Fail to checkout ref: ${commit_ref}"
    exit 1
fi

#------------------#
# pack up packages #
#------------------#

packed_pkgs_dir="${TEMP_DIR}/packages"

mkdir -p "${packed_pkgs_dir}"

echo -e "${H_INFO} 💬 Pack up packages (${commit_sha})..."

# traverse all packages in the repo
for dir in "${repo_dir}/"*/; do
    pushd "${dir}" || exit

    pkg_name=$(basename "${dir}")

    echo -e "${H_DEBUG} 📦 Packaging: ${pkg_name}"

    zip -9rq "${packed_pkgs_dir}/${pkg_name}.sublime-package" . -z <<END
Repository URL: ${PKG_REMOTE_REPO}
Commit SHA: ${commit_sha}
END

    popd || exit
done

#------------------#
# replace packages #
#------------------#

echo -e "${H_INFO} 💬 Update ST packages to '${commit_ref}'..."
cp -rf "${packed_pkgs_dir}"/*.sublime-package "${st_pkgs_dir}"

#----------#
# clean up #
#----------#

echo -e "${H_INFO} 🧹 Clean up..."
rm -rf "${TEMP_DIR}"

#-----#
# end #
#-----#
