#!/bin/bash

set -e -o pipefail
shopt -s nullglob


# This is a configuration/bootstrap file for py.sh.
# https://github.com/etianen/py.sh


# CONFIGURATION SECTION
# Modify these settings to suit your environment.

# URL to py.sh helpers. This should be locked to a specific commit.
export PYSH_HELPERS_URL=${PYSH_HELPERS_URL:="https://github.com/etianen/py.sh/archive/master.tar.gz"}

# The root path of the project. Defaults to the dirname of this script.
export PYSH_ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# The directory to install py.sh into, relative to PYSH_ROOT_PATH.
# This should be excluded from source control.
export PYSH_WORK_DIR=".pysh"


# BOOTSTRAP SECTION
# This should be left as-is.

# Private configuration for py.sh helpers.
export PYSH_SCRIPT=`basename "${BASH_SOURCE[0]}"`
export PYSH_LIB_DIR="lib"
export PYSH_WORK_PATH="${PYSH_ROOT_PATH}/${PYSH_WORK_DIR}"
export PYSH_LIB_PATH="${PYSH_WORK_PATH}/${PYSH_LIB_DIR}"
PYSH_HELPERS_PATH="${PYSH_LIB_PATH}/helpers"

# Download py.sh helpers.
if [ ! -d "${PYSH_HELPERS_PATH}" ]; then
    printf "Downloading py.sh helpers... "
    mkdir -p "${PYSH_HELPERS_PATH}"
    curl --location --silent "${PYSH_HELPERS_URL}" | tar xz --strip-components 1 -C "${PYSH_HELPERS_PATH}"
    printf "done!\n"
fi

# Delegate to the py.sh helpers.
exec "${PYSH_HELPERS_PATH}/pysh-helpers.sh" "${@}"
