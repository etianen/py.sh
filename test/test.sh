#!/bin/bash

# This utility is very difficult to test. Here's at least some attempt at doing so!

set -e -o pipefail
shopt -s nullglob

ROOT_PATH="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"

pysh() {
    echo "TEST: Running ${1}/py.sh ${*:3} with ${2} config."
    "${1}/py.sh" --traceback --env-file="${1}/test/.env" --config-file="${1}/test/package-${2}.json" "${@:3}"
}

assert-standalone-python() {
    pysh ${1} ${2} run python -c "import sys; assert sys.executable == '${1}/.pysh/miniconda/envs/app/bin/python'"
    pysh ${1} ${2} run python -c "import os; assert os.environ['TEST_ENV'] == 'foo'"
}

assert-dep() {
    pysh ${1} ${2} run python -c "import ${3}"
}

# Install an empty package.json.
pysh "${ROOT_PATH}" "missing" install
assert-standalone-python "${ROOT_PATH}" "missing"

# Install a minimal package.json.
pysh "${ROOT_PATH}" "minimal" install
assert-standalone-python "${ROOT_PATH}" "minimal"

# Install a package, with dependencies.
pysh "${ROOT_PATH}" "complete" install
assert-standalone-python "${ROOT_PATH}" "complete"
assert-dep "${ROOT_PATH}" "complete" "psycopg2"
assert-dep "${ROOT_PATH}" "complete" "pytest"
assert-dep "${ROOT_PATH}" "complete" "django"
assert-dep "${ROOT_PATH}" "complete" "flake8"

# Create a standalone distribution.
pysh "${ROOT_PATH}" "complete" dist

# Unzip the standalone distribution.
DIST_PATH="${ROOT_PATH}/dist/pysh-test"
rm -rf "${DIST_PATH}"
unzip -qq -o "${ROOT_PATH}/dist/pysh-test-0.1.0-$(uname -s | tr '[:upper:]' '[:lower:]')-amd64.zip" -d "${DIST_PATH}"

# Install the standalone distribution.
pysh "${DIST_PATH}" "complete" install
assert-standalone-python "${DIST_PATH}" "complete"
assert-dep "${DIST_PATH}" "complete" "psycopg2"
assert-dep "${DIST_PATH}" "complete" "pytest"
assert-dep "${DIST_PATH}" "complete" "django"
assert-dep "${DIST_PATH}" "complete" "flake8"
