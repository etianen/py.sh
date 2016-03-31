#!/bin/bash

set -e -o pipefail
shopt -s nullglob


# This is an automated installer for py.sh.
# https://github.com/etianen/py.sh

# Define some styles.
PLAIN=`printf "\e[0m"`
BOLD=`printf "\e[1m"`
GREEN=`printf "\e[32m"`
CYAN=`printf "\e[36m"`


# Say hello.
printf "Welcome to the ${BOLD}${GREEN}py.sh${PLAIN} automated installer!\n"

# Download the py.sh script.
printf "Downloading py.sh script... "
curl --location --silent "https://raw.githubusercontent.com/etianen/py.sh/master/py.sh" > ./py.sh
printf "${GREEN}done!${PLAIN}\n"

# Make the script executable.
chmod +x ./py.sh

# Update PYSH_HELPERS_URL to point at the latest commit.
# This ensures that the py.sh helpers will remain compatible with the py.sh script.
printf "Configuring py.sh script... "
LATEST_GIT_COMMIT=$(git ls-remote https://github.com/etianen/py.sh.git master | awk '{print $1;}')
sed -i '' 's/https\:\/\/github\.com\/etianen\/py\.sh\/archive\/master\.tar\.gz/https\:\/\/github.com\/etianen\/py.sh\/archive\/'"${LATEST_GIT_COMMIT}"'.tar.gz/g' ./py.sh
printf "${GREEN}done!${PLAIN}\n"

# Run the install command.
./py.sh install

# Say hello.
./py.sh welcome
