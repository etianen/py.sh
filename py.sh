#!/bin/bash

set -e -o pipefail
shopt -s nullglob


# This is a bootstrap file for py.sh.
# https://github.com/etianen/py.sh

# Private configuration for py.sh helpers.
export PYSH_HELPERS_URL=${PYSH_HELPERS_URL:="https://github.com/etianen/py.sh/archive/master.tar.gz"}
export PYSH_ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYSH_SCRIPT_NAME=`basename "${BASH_SOURCE[0]}"`
export PYSH_WORK_PATH="${PYSH_ROOT_PATH}/.pysh"
export PYSH_LIB_PATH="${PYSH_WORK_PATH}/lib"
export PYSH_HELPERS_PATH="${PYSH_LIB_PATH}/helpers"

# Download py.sh helpers.
if [ ! -d "${PYSH_HELPERS_PATH}" ]; then
    printf "Downloading py.sh helpers... "
    mkdir -p "${PYSH_HELPERS_PATH}"
    curl --location --silent "${PYSH_HELPERS_URL}" | tar xz --strip-components 1 -C "${PYSH_HELPERS_PATH}"
    printf "done!\n"
fi

# Delegate to the py.sh helpers.
exec "${PYSH_HELPERS_PATH}/pysh-helpers.sh" "${@}"
