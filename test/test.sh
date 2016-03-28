#!/bin/bash

# This utility is very difficult to test. Here's at least some attempt at doing so!

set -e -o pipefail
shopt -s nullglob

ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
export PYSH_HELPERS_INSTALL_PATH="${ROOT_PATH}"

clean() {
    rm -rf "${1}/.pysh/miniconda"
}

run-test() {
    echo "TEST: Running py.sh ${*:2}"
    "${1}/py.sh" "${@:2}"
}

assert-python() {
    run-test "${1}" run python -c "import sys; assert sys.executable == '${1}/.pysh/miniconda/envs/app/bin/python'"
}

assert-dep() {
    run-test "${1}" run python -c "import ${2}"
}

# Install with no package.json, and some args before the install command.
clean "${ROOT_PATH}"
run-test "${ROOT_PATH}" --traceback install
assert-python "${ROOT_PATH}"

# Install with no package.json, and no args before the install command.
clean "${ROOT_PATH}"
run-test "${ROOT_PATH}" install
assert-python "${ROOT_PATH}"

# Check dotenv file parsing.
run-test "${ROOT_PATH}" --env-file="${ROOT_PATH}/test/.env" run python -c "import os; assert os.environ['TEST_ENV'] == 'foo'"

# Install dependencies from a package.json config file.
run-test "${ROOT_PATH}" --config-file="${ROOT_PATH}/test/package.json" install
assert-python "${ROOT_PATH}"
assert-dep "${ROOT_PATH}" "psycopg2"
assert-dep "${ROOT_PATH}" "pytest"
assert-dep "${ROOT_PATH}" "django"
assert-dep "${ROOT_PATH}" "flake8"

# Create a standalone distribution.
run-test "${ROOT_PATH}" --config-file="${ROOT_PATH}/test/package.json" dist

# Unzip the standalone distribution.
DIST_PATH="${ROOT_PATH}/dist/pysh-test"
rm -rf "${DIST_PATH}"
unzip -qq -o "${ROOT_PATH}/dist/pysh-test-0.1.0-$(uname -s | tr '[:upper:]' '[:lower:]')-amd64.zip" -d "${DIST_PATH}"

# Install the standalone distribution.
echo "NOTICE: About to perform offline tests in 10 seconds."
sleep 10
run-test "${DIST_PATH}" install --offline
assert-python "${DIST_PATH}"
assert-dep "${DIST_PATH}" "psycopg2"
assert-dep "${DIST_PATH}" "django"

# Test clean.
run-test "${DIST_PATH}" clean
if [ -d "${DIST_PATH}/.pysh" ]; then
    echo "Clean did not remove dir!"
    exit 1
fi
