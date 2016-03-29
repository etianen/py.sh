#!/bin/bash

set -e -o pipefail
shopt -s nullglob

# This is a bootstrap file for py.sh.
# https://github.com/etianen/py.sh

# URL to py.sh helpers. This should be locked to a specific commit.
export PYSH_HELPERS_URL=${PYSH_HELPERS_URL:="https://github.com/etianen/py.sh/archive/master.tar.gz"}

# Introspect script environment.
export PYSH_OS_NAME=`uname -s | tr '[:upper:]' '[:lower:]'`
export PYSH_ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYSH_SCRIPT=`basename "${BASH_SOURCE[0]}"`

# Layout of the work dir.
export PYSH_WORK_DIR=".pysh"
export PYSH_LIB_DIR="lib"
export PYSH_MINICONDA_DIR="miniconda"

# Paths for py.sh helpers.
export PYSH_WORK_PATH="${PYSH_ROOT_PATH}/${PYSH_WORK_DIR}"
export PYSH_LIB_PATH="${PYSH_WORK_PATH}/${PYSH_LIB_DIR}"
export PYSH_MINICONDA_PATH="${PYSH_WORK_PATH}/${PYSH_MINICONDA_DIR}"
export PYSH_MINICONDA_BIN_PATH="${PYSH_MINICONDA_PATH}/bin"

# Configuration for py.sh helpers.
export PYSH_CONDA_ENV="app"

# Determine the correct Miniconda installer.
if [ "${PYSH_OS_NAME}" = "darwin" ]; then
    export PYSH_MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
else
    export PYSH_MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
fi

# Local configuration.
export PYSH_HELPERS_PATH="${PYSH_LIB_PATH}/pysh-helpers.tar.gz"
export PYSH_MINICONDA_INSTALLER_PATH="${PYSH_LIB_PATH}/install-miniconda.sh"

# Runs a command silently. In the event of an error, displays the command output.
run-silent() {
    if ! CMD_OUTPUT=$(eval "${@} 2>&1"); then
        printf "ERROR!\n%s\n%s\n" "${*}" "${CMD_OUTPUT}"
        exit 1
    fi
}

# Cleans the py.sh helpers.
clean() {
    printf "Cleaning... "
    rm -rf "${PYSH_WORK_PATH}"
    printf "done!\n"
}

# Downloads py.sh helpers.
download-helpers() {
    if [ ! -f "${PYSH_HELPERS_PATH}" ]; then
        printf "Downloading py.sh helpers... "
        curl --location --silent "${PYSH_HELPERS_URL}" > "${PYSH_HELPERS_PATH}"
        printf "done!\n"
    fi
}

# Downloads Miniconda.
download-miniconda() {
    if [ ! -f "${PYSH_MINICONDA_INSTALLER_PATH}" ]; then
        printf "Downloading Miniconda... "
        curl --location --silent "${PYSH_MINICONDA_INSTALLER_URL}" > "${PYSH_MINICONDA_INSTALLER_PATH}"
        printf "done!\n"
    fi
}

# Installs Miniconda.
install-miniconda() {
    if [ ! -d "${PYSH_MINICONDA_PATH}" ]; then
        printf "Installing Miniconda... "
        run-silent bash "${PYSH_MINICONDA_INSTALLER_PATH}" -b -p "${PYSH_MINICONDA_PATH}"
        printf "done!\n"
        # Install helpers.
        printf "Installing py.sh helpers... "
        run-silent "${PYSH_MINICONDA_BIN_PATH}/pip" install --no-index --upgrade "${PYSH_HELPERS_PATH}"
        printf "done!\n"
    fi
}

# Installs everything.
install() {
    mkdir -p "${PYSH_LIB_PATH}"
    download-helpers
    download-miniconda
    install-miniconda
}

# Checks that the install is present.
verify-install() {
    if [ ! -d "${PYSH_MINICONDA_PATH}" ]; then
        printf "ERROR!\nRun ${PYSH_SCRIPT} install before running other commands.\n"
        exit 1
    fi
}

# Parse the first positional argument.
while getopts ":" OPT ; do : ; done
COMMAND="${!OPTIND}"

# Handle commands that don't need Python.
case "${COMMAND}" in
    clean)
        clean
        exit 0
        ;;
    install)
        install
        ;;
    *)
        verify-install
        ;;
esac

# Delegate to the Python py.sh helpers.
exec "${PYSH_MINICONDA_BIN_PATH}/python" -m _pysh "${@}"
