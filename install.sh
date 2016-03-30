#!/bin/bash

set -e -o pipefail
shopt -s nullglob


# This is an automated installer for py.sh.
# https://github.com/etianen/py.sh

# Download the py.sh script.
curl --location --silent "https://raw.githubusercontent.com/etianen/py.sh/master/py.sh" > py.sh

# Make the script executable.
chmod +x py.sh

# Update PYSH_HELPERS_URL to point at the latest commit.
# This ensures that the py.sh helpers will remain compatible with the py.sh script.
LATEST_GIT_COMMIT=$(git ls-remote https://github.com/etianen/py.sh.git master | awk '{print $1;}')
sed -i '' 's/https\:\/\/github\.com\/etianen\/py\.sh\/archive\/master\.tar\.gz/https\:\/\/github.com\/etianen\/py.sh\/archive\/'"${LATEST_GIT_COMMIT}"'.tar.gz/g' py.sh

# Run the install command.
py.sh install

# Print some useful information.
cat << EOF
                   _
                  | |
 _ __  _   _   ___| |__
| '_ \| | | | / __| '_ \\
| |_) | |_| |_\__ \ | | |
| .__/ \__, (_)___/_| |_|
| |     __/ |
|_|    |___/

py.sh is now installed!

A standalone Python interpreter has been installed into \`.pysh\`.
Recommended: Add \`.pysh\` to your \`.gitignore\` file.

Use \`./py.sh\` to manage your environment.
Hint: You can learn a lot from \`./py.sh --help\` and \`./py.sh <command name> --help\`.

EOF
