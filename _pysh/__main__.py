"""
py.sh helpers.
"""

import argparse
import os
import sys
from _pysh.commands import install, dist, activate, run
from _pysh.tasks import capture_errors


def main(args, environ):
    # Create a parser.
    parser = argparse.ArgumentParser(
        prog=environ.pop("PYSH_SCRIPT"),
        description="Install and manage a standalone Python interpreter and environment.",
    )
    parser.add_argument(
        "--conda-env",
        default="app",
        help="The name of the conda environment to install the app into."
    )
    parser.add_argument(
        "--config-file",
        default="package.json",
        help="Path to a JSON config file.",
    )
    parser.add_argument(
        "--env-file",
        default=".env",
        help="Path to a .env file, to be sourced before running any commands.",
    )
    parser.add_argument(
        "--shell",
        default="/bin/bash",
        help="The shell to use to run scripts in this environment.",
    )
    parser.add_argument(
        "--traceback",
        default=False,
        action="store_true",
        help="Enable tracebacks in errors.",
    )
    parser.set_defaults(
        os_name=environ.pop("PYSH_OS_NAME"),
        root_path=environ.pop("PYSH_ROOT_PATH"),
        pysh_dir=environ.pop("PYSH_DIR"),
        miniconda_dir=environ.pop("PYSH_MINICONDA_DIR"),
        lib_dir=environ.pop("PYSH_LIB_DIR"),
    )
    command_parsers = parser.add_subparsers(
        title="subcommands",
        help="The command to run.",
    )
    # Install command.
    install_parser = command_parsers.add_parser(
        "install",
        help="Installs a standalone Python interpreter and all the app dependencies.",
    )
    install_parser.add_argument(
        "--offline",
        default=False,
        action="store_true",
        help="Install dependencies from a local archive. Implies --production.",
    )
    install_parser.add_argument(
        "--production",
        default=False,
        action="store_true",
        help="Don't install development dependencies.",
    )
    install_parser.set_defaults(func=install)
    # Dist command.
    dist_parser = command_parsers.add_parser(
        "dist",
        help="Creates a standalone archive of this app and all it's dependencies.",
    )
    dist_parser.add_argument(
        "--dist-dir",
        default="dist",
        help="The directory name to write archive files to.",
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
    run_parser.add_argument(
        nargs="+",
        dest="local_command",
        metavar="local-command",
        help="The local environment shell command to run.",
    )
    run_parser.set_defaults(func=run)
    # Parse the args.
    opts, unknown_args = parser.parse_known_args(args)
    # Run the command.
    with capture_errors(opts):
        opts.func(opts, unknown_args)


if __name__ == "__main__":
    main(sys.argv[1:], os.environ)
