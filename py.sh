#!/bin/bash
set -e -o pipefail
shopt -s nullglob


# Shared environment.

export PYSH_OS_NAME=`uname -s | tr '[:upper:]' '[:lower:]'`
export PYSH_ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYSH_SCRIPT=`basename "${BASH_SOURCE[0]}"`
export PYSH_DIR=".pysh"
export PYSH_MINICONDA_DIR="miniconda"


# Local environment.

PYSH_DIR_PATH="${PYSH_ROOT_PATH}/${PYSH_DIR}"
MINICONDA_DIR_PATH="${PYSH_DIR_PATH}/${PYSH_MINICONDA_DIR}"


# Helpers.

run-silent() {
    if ! CMD_OUTPUT=$(eval "${@} 2>&1"); then
        printf "ERROR!\n%s\n%s\n" "${*}" "${CMD_OUTPUT}"
        exit 1
    fi
}

activate-env() {
    # Miniconda setup.
    run-silent source "${MINICONDA_DIR_PATH}/bin/activate" "${1}"
    # Read local env.
    local ENV_FILE_PATH="${PYSH_ROOT_PATH}/.env"
    if [ -f "${ENV_FILE_PATH}" ]; then
        run-silent source "${ENV_FILE_PATH}"
    fi
}


# Commands.

clean() {
    printf "Cleaning... "
    rm -rf "${PYSH_ROOT_PATH}/${PYSH_DIR}"
    printf "done!\n"
}

install() {
    local MINICONDA_INSTALLER_PATH="${PYSH_DIR_PATH}/install-miniconda.sh"
    local PYSH_HELPERS_URL=${PYSH_HELPERS_URL:="https://github.com/etianen/py.sh/archive/master.tar.gz"}
    local PYSH_HELPERS_PATH="${PYSH_DIR_PATH}/pysh-helpers.tar.gz"
    local PYSH_HELPERS_INSTALL_PATH=${PYSH_HELPERS_INSTALL_PATH:="${PYSH_HELPERS_PATH}"}
    # Download Miniconda.
    if [ ! -f "${MINICONDA_INSTALLER_PATH}" ]; then
        printf "Downloading Miniconda... "
        if [ "${PYSH_OS_NAME}" = "darwin" ]; then
            local MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
        else
            local MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        fi
        mkdir -p "${PYSH_DIR_PATH}"
        curl --location --silent "${MINICONDA_INSTALLER_URL}" > "${MINICONDA_INSTALLER_PATH}"
        printf "done!\n"
    fi
    # Download py.sh helpers.
    if [ ! -f "${PYSH_HELPERS_PATH}" ]; then
        printf "Downloading py.sh helpers... "
        curl --location --silent "${PYSH_HELPERS_URL}" > "${PYSH_HELPERS_PATH}"
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
}

activate() {
    # Activate the environment.
    printf "Activating environment... "
    activate-env
    printf "done!\n"
    # All done!
    printf "Deactivate environment with 'exit' or [Ctl+D].\n"
    export PS1="($(package-id)) \h:\W \u\$ "
    exec bash
}


# Run commands that do not require the installation to be complete.

if [ "${1}" = "clean" ]; then
    clean
    exit 0
elif [ "${1}" = "install" ]; then
    install
fi


# Ensure installation is complete.

if [ ! -d "${MINICONDA_DIR_PATH}" ]; then
    printf "ERROR!\nRun ./${PYSH_SCRIPT} install before attempting other commands.\n"
    exit 1
fi


# Delegate to py.sh helpers.

"${MINICONDA_DIR_PATH}/bin/python" -m _pysh "${@}"


# Run commands that require bash.

if [ "${1}" = "activate" ]; then
    activate
elif [ "${1}" = "run" ]; then
    activate-env
    exec "${@}"
fi
