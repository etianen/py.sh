#!/bin/bash

set -e -o pipefail
shopt -s nullglob

# This is the helper script for py.sh.
# It's a minimal shell script designed to get a functioning Python environment onto the system.
# Once Python is installed, it delegates all responsibility to the Python script.

# Configuration for the py.sh helpers.
export PYSH_OS_NAME=`uname -s | tr '[:upper:]' '[:lower:]'`
export PYSH_MINICONDA_DIR="miniconda"
export PYSH_LIB_DIR="lib"
export PYSH_CONDA_ENV="app"

# Paths for the py.sh helpers.
export PYSH_MINICONDA_PATH="${PYSH_WORK_PATH}/${PYSH_MINICONDA_DIR}"
export PYSH_MINICONDA_BIN_PATH="${PYSH_MINICONDA_PATH}/bin"
export PYSH_LIB_PATH="${PYSH_WORK_PATH}/${PYSH_LIB_DIR}"

MINICONDA_INSTALLER_PATH="${PYSH_LIB_PATH}/install-miniconda.sh"

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

# Downloads Miniconda.
download-miniconda() {
    if [ ! -f "${MINICONDA_INSTALLER_PATH}" ]; then
        # Determine the correct Miniconda installer.
        if [ "${PYSH_OS_NAME}" = "darwin" ]; then
            local MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
        else
            local MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
        fi
        # Download the installer.
        printf "Downloading Miniconda... "
        mkdir -p "${PYSH_LIB_PATH}"
        curl --location --silent "${MINICONDA_INSTALLER_URL}" > "${MINICONDA_INSTALLER_PATH}"
        printf "done!\n"
    fi
}

# Installs Miniconda.
install-miniconda() {
    if [ ! -d "${PYSH_MINICONDA_PATH}" ]; then
        printf "Installing Miniconda... "
        run-silent bash "${MINICONDA_INSTALLER_PATH}" -b -p "${PYSH_MINICONDA_PATH}"
        printf "done!\n"
        # Install helpers.
        printf "Installing py.sh helpers... "
        run-silent "${PYSH_MINICONDA_BIN_PATH}/pip" install --no-index --upgrade "${PYSH_HELPERS_PATH}"
        printf "done!\n"
    fi
}

# Installs everything.
install() {
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
