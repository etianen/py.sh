#!/bin/bash

set -e -o pipefail
shopt -s nullglob


# This is an automated installer for py.sh.
# https://github.com/etianen/py.sh

# Download the py.sh script, and update the helper URL with the latest commit.
curl --location --silent "https://raw.githubusercontent.com/etianen/py.sh/master/py.sh" > py.sh

# Make the script executable.
chmod +x py.sh

# Update PYSH_HELPERS_URL to point at a specific commit.
# This ensures that the py.sh helpers will remain compatible with the py.sh script.
LATEST_GIT_COMMIT=$(git ls-remote https://github.com/etianen/py.sh.git master | awk '{print $1;}')
sed -i '' 's/https\:\/\/github\.com\/etianen\/py\.sh\/archive\/master\.tar\.gz/https\:\/\/github.com\/etianen\/py.sh\/archive\/'"${LATEST_GIT_COMMIT}"'.tar.gz/g' py.sh

# Run the install command.
py.sh install

# Print some useful information.
echo
echo "py.sh is now installed!"
echo
echo "A standalone Python interpreter has been installed into \`./.pysh\`."
echo "Recommended: Add \`.pysh\` to your \`.gitignore\` file."
echo
echo "Use \`./py.sh\` to manage your environment."
echo "Hint: You can learn a lot from \`./py.sh --help\` and \`./py.sh <command name> --help\`."
echo
