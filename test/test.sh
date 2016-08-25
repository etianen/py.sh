#!/bin/bash

set -e -o pipefail
shopt -s nullglob

# This utility is very difficult to test. Here's at least some attempt at doing so!

# Load the styles.
source "$( dirname "${BASH_SOURCE[0]}" )/../pysh-styles.sh"

ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

# Make a temporary local copy of the py.sh helpers.
TMP_HELPERS_ARCHIVE=`mktemp`
export PYSH_HELPERS_URL="file://${TMP_HELPERS_ARCHIVE}"
(cd "${ROOT_PATH}" && git archive HEAD --format="tar" --prefix="export/") | gzip > "${TMP_HELPERS_ARCHIVE}"
trap "rm ${TMP_HELPERS_ARCHIVE}" exit

# Remove any existing helpers.
rm -rf "${ROOT_PATH}/.pysh"

clean() {
    rm -rf "${1}/.pysh/miniconda"
}

run-test() {
    printf "${PYSH_STYLE_CODE}TEST:${PYSH_STYLE_PLAIN} Running py.sh ${*:2}\n"
    "${1}/py.sh" --traceback "${@:2}"
}

assert-python() {
    run-test "${1}" run python -c "import sys; assert sys.executable == '${1}/.pysh/miniconda/envs/app/bin/python'"
}

assert-dep() {
    run-test "${1}" run python -c "import ${2}"
}

# Install requirements files.
clean "${ROOT_PATH}"
run-test "${ROOT_PATH}" install
assert-python "${ROOT_PATH}"

# Say hello.
run-test "${ROOT_PATH}" welcome

# Run flake8
run-test "${ROOT_PATH}" run pip install flake8
run-test "${ROOT_PATH}" run flake8 _pysh

REQUIREMENTS_ARGS="
--requirements-conda-file=${ROOT_PATH}/test/requirements-conda.txt
--requirements-conda-dev-file=${ROOT_PATH}/test/requirements-conda-dev.txt
--requirements-file=${ROOT_PATH}/test/requirements.txt
--requirements-dev-file=${ROOT_PATH}/test/requirements-dev.txt
"

# Install dependencies from an environment file config file.
run-test "${ROOT_PATH}" ${REQUIREMENTS_ARGS} install
assert-python "${ROOT_PATH}"
assert-dep "${ROOT_PATH}" "psycopg2"
assert-dep "${ROOT_PATH}" "pytest"
assert-dep "${ROOT_PATH}" "django"
assert-dep "${ROOT_PATH}" "flake8"

# Create a standalone distribution.
run-test "${ROOT_PATH}" ${REQUIREMENTS_ARGS} dist

# Unzip the standalone distribution.
DIST_PATH="${ROOT_PATH}/dist/pysh-test"
rm -rf "${DIST_PATH}"
unzip -qq -o "${ROOT_PATH}/dist/app.zip" -d "${DIST_PATH}"

printf "${PYSH_STYLE_CODE}NOTICE:${PYSH_STYLE_PLAIN} About to perform offline tests in 10 seconds.\n"
sleep 10

# Install the standalone distribution.
run-test "${DIST_PATH}" ${REQUIREMENTS_ARGS} install --offline
assert-python "${DIST_PATH}"
assert-dep "${DIST_PATH}" "psycopg2"
assert-dep "${DIST_PATH}" "django"

# Cleanup.
rm -rf "${DIST_PATH}"
printf "${PYSH_STYLE_CODE}NOTICE:${PYSH_STYLE_PLAIN} All tests pass!\n"
