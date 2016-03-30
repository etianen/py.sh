#!/bin/bash

# This utility is very difficult to test. Here's at least some attempt at doing so!

set -e -o pipefail
shopt -s nullglob

ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

# Define some colors.
RED=`printf "\e[32m"`
BOLD=`printf "\e[1m"`
CYAN=`printf "\e[36m"`
PLAIN=`printf "\e[0m"`

# Make a temporary local copy of the py.sh helpers.
TMP_HELPERS_ARCHIVE=`mktemp`
export PYSH_HELPERS_URL="file://${TMP_HELPERS_ARCHIVE}"
(cd "${ROOT_PATH}" && git archive HEAD --format="tar" --prefix="export/") | gzip > "${TMP_HELPERS_ARCHIVE}"
trap "rm ${TMP_HELPERS_ARCHIVE}" exit

clean() {
    rm -rf "${1}/.pysh/miniconda"
    rm -rf "${1}/.pysh/lib/helpers"
}

run-test() {
    printf "${BOLD}${CYAN}TEST:${PLAIN} Running py.sh ${*:2}\n"
    "${1}/py.sh" "${@:2}"
}

assert-python() {
    run-test "${1}" --traceback run python -c "import sys; assert sys.executable == '${1}/.pysh/miniconda/envs/app/bin/python'"
}

assert-dep() {
    run-test "${1}" --traceback run python -c "import ${2}"
}

# Install with no package.json.
clean "${ROOT_PATH}"
run-test "${ROOT_PATH}" --traceback install
assert-python "${ROOT_PATH}"

# Run flake8
run-test "${ROOT_PATH}" run pip install flake8
run-test "${ROOT_PATH}" run flake8 _pysh

# Check dotenv file parsing.
run-test "${ROOT_PATH}" --traceback --env-file="${ROOT_PATH}/test/.env" run python -c "import os; assert os.environ['TEST_ENV'] == 'foo'"

# Install dependencies from a package.json config file.
run-test "${ROOT_PATH}" --traceback --config-file="${ROOT_PATH}/test/package.json" install
assert-python "${ROOT_PATH}"
assert-dep "${ROOT_PATH}" "psycopg2"
assert-dep "${ROOT_PATH}" "pytest"
assert-dep "${ROOT_PATH}" "django"
assert-dep "${ROOT_PATH}" "flake8"

# Create a standalone distribution.
run-test "${ROOT_PATH}" --traceback --config-file="${ROOT_PATH}/test/package.json" dist

# Unzip the standalone distribution.
DIST_PATH="${ROOT_PATH}/dist/pysh-test"
rm -rf "${DIST_PATH}"
unzip -qq -o "${ROOT_PATH}/dist/pysh-test-0.1.0-$(uname -s | tr '[:upper:]' '[:lower:]')-amd64.zip" -d "${DIST_PATH}"

# Install the standalone distribution.
printf "${BOLD}${CYAN}NOTICE:${PLAIN} About to perform offline tests in 10 seconds.\n"
sleep 10
run-test "${DIST_PATH}" --traceback --config-file="${DIST_PATH}/test/package.json" install --offline
assert-python "${DIST_PATH}"
assert-dep "${DIST_PATH}" "psycopg2"
assert-dep "${DIST_PATH}" "django"

# Test clean.
run-test "${DIST_PATH}" clean
if [ -d "${DIST_PATH}/.pysh" ]; then
    echo "${BOLD}${RED}ERROR:${PLAIN} Clean did not remove dir!"
    exit 1
fi

# Cleanup.
rm -rf "${DIST_PATH}"
