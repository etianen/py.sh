#!/bin/bash

set -e -o pipefail
shopt -s nullglob


# Runs a command silently. In the event of an error, displays the command output.
run-silent() {
    if ! CMD_OUTPUT=$(eval "${@} 2>&1"); then
        printf "ERROR!\n%s\n%s\n" "${*}" "${CMD_OUTPUT}"
        exit 1
    fi
}
