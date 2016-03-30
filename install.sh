#!/bin/bash

set -e -o pipefail
shopt -s nullglob


# This is an automated installer for py.sh.
# https://github.com/etianen/py.sh

# Define some colors.
GREEN=`printf "\e[32m"`
BOLD=`printf "\e[1m"`
CYAN=`printf "\e[36m"`
PLAIN=`printf "\e[0m"`

# Say hello.
printf "Welcome to the ${BOLD}py.sh${PLAIN} automated installer!\n"

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

# Print some useful information.
cat << EOF
${GREEN}                   _
                  | |
 _ __  _   _   ___| |__
| '_ \| | | | / __| '_ \\
| |_) | |_| |_\__ \ | | |
| .__/ \__, (_)___/_| |_|
| |     __/ |
|_|    |___/
${PLAIN}
${BOLD}py.sh${PLAIN} is now installed!

A standalone Python interpreter has been installed into ${CYAN}.pysh${PLAIN}.
${BOLD}Recommended:${PLAIN} Add ${CYAN}.pysh${PLAIN} to your ${CYAN}.gitignore${PLAIN} file.

Use ${CYAN}./py.sh${PLAIN} to manage your environment.
${BOLD}Hint:${PLAIN} You can learn a lot from ${CYAN}./py.sh --help${PLAIN} and ${CYAN}./py.sh <command name> --help${PLAIN}.

EOF
