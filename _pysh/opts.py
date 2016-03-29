import argparse
import os
from _pysh.commands import install, dist, activate, run
from _pysh.constants import CONFIG_PREFIX


# The main argument parser.
parser = argparse.ArgumentParser(
    prog=os.environ["PYSH_SCRIPT"],
    description="Install and manage a standalone Python interpreter and environment.",
)

parser.add_argument(
    "--conda-env",
    default="app",
    help="The name of the conda environment to install the app into. Defaults to 'app'.",
)

parser.add_argument(
    "--config-file",
    default="package.json",
    help="Path to a JSON config file. Defaults to 'package.json' in the same directory as this script.",
)

parser.add_argument(
    "--env-file",
    default=".env",
    help=(
        "Path to a file that will be sourced before running any environment commands. "
        "Defaults to '.env' file in the same directory as the script"
    ),
)

parser.add_argument(
    "--shell",
    default="/bin/bash",
    help="The shell to use to run scripts in this environment. Defaults to '/bin/bash'.",
)

parser.add_argument(
    "--traceback",
    default=False,
    action="store_true",
    help="Enable tracebacks in errors.",
)

parser.set_defaults(**{
    key[len(CONFIG_PREFIX):].lower(): value
    for key, value
    in os.environ.items()
    if key.startswith(CONFIG_PREFIX)
})

command_parsers = parser.add_subparsers(
    title="subcommands",
    help="The command to run.",
)


# Install parser.

install_parser = command_parsers.add_parser(
    "install",
    help="Installs a standalone Python interpreter and all the app dependencies.",
)

install_parser.add_argument(
    "--offline",
    default=False,
    action="store_true",
    help=(
        "Install dependencies from a standalone archive. Implies --production. "
        "This should only be run in an archive created using the 'dist' command."
    ),
)

install_parser.add_argument(
    "--production",
    default=False,
    action="store_true",
    help="Don't install development dependencies.",
)

install_parser.set_defaults(func=install)


# Dist parser.

dist_parser = command_parsers.add_parser(
    "dist",
    help="Creates a standalone archive of this app and all it's dependencies.",
)

dist_parser.add_argument(
    "--dist-dir",
    default="dist",
    help="The directory name to write archive files to. Defaults to 'dist'.",
)

dist_parser.set_defaults(func=dist, production=False, conda_env="build", offline=False)


# Activate command.

activate_parser = command_parsers.add_parser(
    "activate",
    help="Activates the standalone Python environment.",
)

activate_parser.set_defaults(func=activate)


# Run command.

run_parser = command_parsers.add_parser(
    "run",
    help="Runs shell command in the standalone Python environment.",
)

run_parser.set_defaults(func=run)


# Parses the options.

def parse_args(args):
    return parser.parse_known_args(args)
