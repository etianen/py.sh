#!/bin/bash

set -e -o pipefail
shopt -s nullglob

# Define some styles.
if [ -t 1 ]; then
    define-style() {
        printf "\e[%sm\n" ${1}
    }
else
    define-style() {
        :
    }
fi

PLAIN=`define-style "0"`
BOLD=`define-style "1"`
RED=`define-style "31"`
GREEN=`define-style "32"`

# Script environment.
export PYSH_OS_NAME=`uname -s | tr '[:upper:]' '[:lower:]'`

# Paths for py.sh helpers.
export PYSH_MINICONDA_PATH="${PYSH_WORK_PATH}/miniconda"
export PYSH_MINICONDA_BIN_PATH="${PYSH_MINICONDA_PATH}/bin"

# Paths for this script.
PYSH_MINICONDA_INSTALLER_PATH="${PYSH_LIB_PATH}/install-miniconda.sh"

# Determine the correct Miniconda installer.
if [ "${PYSH_OS_NAME}" = "darwin" ]; then
    PYSH_MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-MacOSX-x86_64.sh"
else
    PYSH_MINICONDA_INSTALLER_URL="https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh"
fi

# Runs a script silently, only outputing stderr/stdout on failure.
run-silent() {
    if ! CMD_OUTPUT=$(eval "${@} 2>&1"); then
        printf "${RED}ERROR!${PLAIN}\n%s\n%s\n" "${*}" "${CMD_OUTPUT}"
        exit 1
    fi
}

# Download Miniconda.
if [ ! -f "${PYSH_MINICONDA_INSTALLER_PATH}" ]; then
    # Download Miniconda.
    printf "Downloading Miniconda... "
    curl --location --silent "${PYSH_MINICONDA_INSTALLER_URL}" > "${PYSH_MINICONDA_INSTALLER_PATH}"
    printf "${GREEN}done!${PLAIN}\n"
fi

# Install Miniconda.
if [ ! -d "${PYSH_MINICONDA_PATH}" ]; then
    printf "Installing Miniconda... "
    run-silent bash "${PYSH_MINICONDA_INSTALLER_PATH}" -b -p "${PYSH_MINICONDA_PATH}"
    printf "${GREEN}done!${PLAIN}\n"
    # Install helpers.
    printf "Installing py.sh helpers... "
    run-silent "${PYSH_MINICONDA_BIN_PATH}/pip" install --no-index --upgrade "${PYSH_HELPERS_PATH}"
    printf "${GREEN}done!${PLAIN}\n"
fi

# Delegate to Python py.sh helpers.
exec "${PYSH_MINICONDA_BIN_PATH}/python" -m _pysh "${@}"
