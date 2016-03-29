#!/bin/bash

set -e -o pipefail
shopt -s nullglob

# This is a bootstrap/configuration file for py.sh.
# https://github.com/etianen/py.sh


# CONFIGURATION SECTION.
# This section can be modified to configure your py.sh environment.

# The full root path of the project. Defaults to the directory of this script.
export PYSH_ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# The directory used to contain py.sh metadata, relative to PYSH_ROOT_PATH.
# This should be excluded from source control.
export PYSH_WORK_DIR=".pysh"

# Path to the .tar.gz file containing the py.sh helpers.
export PYSH_HELPERS_URL=${PYSH_HELPERS_URL:="https://github.com/etianen/py.sh/archive/master.tar.gz"}


# BOOTSTRAP SECTION.
# This section should be left as-is.

# Private configuration for the py.sh helpers.
export PYSH_SCRIPT=`basename "${BASH_SOURCE[0]}"`
export PYSH_HELPERS_DIR="helpers"
export PYSH_WORK_PATH="${PYSH_ROOT_PATH}/${PYSH_WORK_DIR}"
export PYSH_HELPERS_PATH="${PYSH_WORK_PATH}/${PYSH_HELPERS_DIR}"

# Download py.sh helper scripts.
mkdir -p "${PYSH_WORK_PATH}"
if [ ! -d "${PYSH_HELPERS_PATH}" ]; then
    printf "Downloading py.sh helpers... "
    mkdir -p "${PYSH_HELPERS_PATH}"
    curl --location --silent "${PYSH_HELPERS_URL}" | tar xz --strip-components 1 -C "${PYSH_HELPERS_PATH}"
    printf "done!\n"
fi

# Delegate to the py.sh helper scripts.
exec "${PYSH_HELPERS_PATH}/pysh-helpers.sh" "${@}"
