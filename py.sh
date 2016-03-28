#!/bin/bash

set -e -o pipefail
shopt -s nullglob

export PYSH_OS_NAME=`uname -s | tr '[:upper:]' '[:lower:]'`
export PYSH_ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYSH_SCRIPT=`basename "${BASH_SOURCE[0]}"`
export PYSH_DIR=".pysh"
export PYSH_MINICONDA_DIR="miniconda"
export PYSH_LIB_DIR="lib"

PYSH_DIR_PATH="${PYSH_ROOT_PATH}/${PYSH_DIR}"
PYSH_LIB_PATH="${PYSH_DIR_PATH}/${PYSH_LIB_DIR}"
MINICONDA_DIR_PATH="${PYSH_DIR_PATH}/${PYSH_MINICONDA_DIR}"
MINICONDA_INSTALLER_PATH="${PYSH_LIB_PATH}/install-miniconda.sh"
PYSH_HELPERS_PATH="${PYSH_LIB_PATH}/pysh-helpers.tar.gz"
PYSH_HELPERS_INSTALL_PATH=${PYSH_HELPERS_INSTALL_PATH:="${PYSH_HELPERS_PATH}"}

if [ "${PYSH_OS_NAME}" = "darwin" ]; then
    MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
else
    MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
fi

run-silent() {
    if ! CMD_OUTPUT=$(eval "${@} 2>&1"); then
        printf "ERROR!\n%s\n%s\n" "${*}" "${CMD_OUTPUT}"
        exit 1
    fi
}

if [[ "${*}" =~ (^| )([^- ][^ ]+) ]]; then
    if [ "${BASH_REMATCH[2]}" == "clean" ]; then
        printf "Cleaning... "
        rm -rf "${PYSH_ROOT_PATH}/${PYSH_DIR}"
        printf "done!\n"
        exit 0
    elif [ "${BASH_REMATCH[2]}" == "install" ]; then
        # Download Miniconda.
        if [ ! -f "${MINICONDA_INSTALLER_PATH}" ]; then
            printf "Downloading Miniconda... "
            mkdir -p "${PYSH_LIB_PATH}"
            curl --location --silent "${MINICONDA_INSTALLER_URL}" > "${MINICONDA_INSTALLER_PATH}"
            printf "done!\n"
        fi
        # Download py.sh helpers.
        if [ ! -f "${PYSH_HELPERS_PATH}" ]; then
            printf "Downloading py.sh helpers... "
            curl --location --silent "https://github.com/etianen/py.sh/archive/master.tar.gz" > "${PYSH_HELPERS_PATH}"
            printf "done!\n"
        fi
        # Install Miniconda.
        if [ ! -d "${MINICONDA_DIR_PATH}" ]; then
            printf "Installing Miniconda... "
            run-silent bash "${MINICONDA_INSTALLER_PATH}" -b -p "${MINICONDA_DIR_PATH}"
            printf "done!\n"
            # Install helpers.
            printf "Installing py.sh helpers... "
            run-silent "${MINICONDA_DIR_PATH}/bin/pip" install --no-index --upgrade "${PYSH_HELPERS_INSTALL_PATH}"
            printf "done!\n"
        fi
    fi
fi

if [ ! -d "${MINICONDA_DIR_PATH}" ]; then
    printf "ERROR!\nRun ./${PYSH_SCRIPT} install before running other commands.\n"
    exit 1
fi

exec "${MINICONDA_DIR_PATH}/bin/python" -m _pysh "${@}"
