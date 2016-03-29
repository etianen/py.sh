#!/bin/bash

set -e -o pipefail
shopt -s nullglob


# This is a generator file for py.sh.
# https://github.com/etianen/py.sh

# Get the latest commit from GitHub.
GIT_COMMIT=$(git ls-remote https://github.com/etianen/py.sh.git master | awk '{print $1;}')

# Pull in the py.sh template url, and update the helper URL with the latest commit.
curl --location --silent "https://raw.githubusercontent.com/etianen/py.sh/master/py.sh" | sed 's/https\:\/\/github\.com\/etianen\/py\.sh\/archive\/master\.tar\.gz/https\:\/\/github.com\/etianen\/py.sh\/archive\/'"${GIT_COMMIT}"'.tar.gz/g'
