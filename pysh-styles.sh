# Style definitions for py.sh.

if [ -t 1 ]; then
    export PYSH_STYLE_PLAIN="\033[0m"
    export PYSH_STYLE_SUCCESS="\033[32m"
    export PYSH_STYLE_ERROR="\033[31m"
    export PYSH_STYLE_WARN="\033[33m"
    export PYSH_STYLE_CODE="\033[36m"
fi
