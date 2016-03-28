"""
py.sh helpers.
"""

import argparse
from contextlib import contextmanager
import json
import os
import shlex
import signal
import subprocess
import sys
import traceback


# Shared environment.

PYSH_OS_NAME = os.environ["PYSH_OS_NAME"]
PYSH_ROOT_PATH = os.environ["PYSH_ROOT_PATH"]
PYSH_SCRIPT = os.environ["PYSH_SCRIPT"]
PYSH_DIR = os.environ["PYSH_DIR"]
PYSH_MINICONDA_DIR = os.environ["PYSH_MINICONDA_DIR"]


# Local environment.

PYSH_DIR_PATH = os.path.join(PYSH_ROOT_PATH, PYSH_DIR)


# Tasks.

class TaskError(Exception):

    pass


class TaskWarning(Exception):

    pass


@contextmanager
def capture_errors(opts):
    try:
        yield
    except TaskWarning as ex:
        sys.stdout.write("WARNING!\n")
        sys.stdout.write("* {}\n".format(ex.args[0]))
    except KeyboardInterrupt:
        sys.stdout.write("ABORTED!\n")
        sys.exit(1)
    except Exception as ex:
        sys.stdout.write("ERROR!\n")
        sys.stdout.write("> {}\n".format(ex.args[0] if isinstance(ex, TaskError) else "Unexpected error."))
        if opts.traceback:
            traceback.print_exc(file=sys.stdout)
        sys.exit(1)
    finally:
        sys.stdout.flush()


@contextmanager
def mark_task(opts, description):
    sys.stdout.write("{}... ".format(description))
    sys.stdout.flush()
    with capture_errors(opts):
        yield
        sys.stdout.write("done!\n")


# Commands.

def shell(command, **kwargs):
    # Escape the kwargs.
    quoted_kwargs = {
        key: shlex.quote(value) if isinstance(value, str) else " ".join(map(shlex.quote, value))
        for key, value
        in kwargs.items()
    }
    quoted_command = command.format(**quoted_kwargs)
    # Create the environment.
    env = os.environ.copy()
    env["PATH"] = "{}:{}".format(os.path.join(PYSH_DIR_PATH, PYSH_MINICONDA_DIR, "bin"), os.environ.get("PATH", ""))
    # Run the command.
    process = subprocess.Popen(
        quoted_command,
        env=env,
        executable="/bin/bash",
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # Wait for completion.
    try:
        (stdout, stderr) = process.communicate()
    except KeyboardInterrupt:
        process.send_signal(signal.SIGINT)
        process.communicate()
        raise
    if process.returncode != 0:
        raise TaskError("{} crashed.\n{}{}".format(quoted_command, stdout.decode("latin1"), stderr.decode("latin1")))
    return stdout


# Config.

class Config:

    def __init__(self, value, path):
        self.value = value
        self._path = []
        if not isinstance(value, dict):
            raise ValueError("Expected config data to be a dict.")

    def get(self, name, default):
        value = self.value.get(name, default)
        if value.__class__ != default.__class__:
            raise TaskError("Expected config {} to be a {}.".format(".".join(self._path, default.__class__.__name__)))
        if isinstance(value, dict):
            return Config(value, self._path + [name])
        return value


def load_config(opts):
    with mark_task(opts, "Loading config from {}".format(opts.config)):
        package_json_path = os.path.join(PYSH_ROOT_PATH, opts.config)
        if os.path.exists(package_json_path):
            with open(package_json_path, "rb") as package_json_handle:
                try:
                    return Config(json.loads(package_json_handle.read().decode("utf-8")), [])
                except ValueError:
                    raise TaskError("Invalid {} config file.".format(opts.config))
        else:
            raise TaskWarning("Missing {} config file.".format(opts.config))
    # Provide a fallback config.
    return Config({}, [])


# Conda.

def delete_conda_env(opts, env_name):
    with mark_task(opts, "Cleaning {} environment".format(env_name)):
        shell("conda env remove --yes --name {env_name}", env_name=env_name)


def reset_conda_env(config, opts, env_name):
    delete_conda_env(opts, env_name)
    # Create a new env.
    python_version = config.get("pysh", {}).get("version", "3")
    with mark_task(opts, "Installing {} Python {}".format(env_name, python_version)):
        shell(
            "conda create --yes --name {env_name} python={python_version}",
            env_name=env_name,
            python_version=python_version,
        )


# Commands.

def install(opts):
    config = load_config(opts)
    reset_conda_env(config, opts, "app")


COMMANDS = {
    "install": install,
}


# Main method.

parser = argparse.ArgumentParser(
    prog=PYSH_SCRIPT,
    description="Install and manage a standalone Python interpreter and environment.",
)
parser.add_argument(
    "command",
    choices=frozenset(COMMANDS.keys()),
    help="The command to run.",
)
parser.add_argument(
    "--config",
    default="package.json",
    help="Path to a JSON config file.",
)
parser.add_argument(
    "--traceback",
    default=False,
    action="store_true",
    help="Enable tracebacks in errors.",
)


def main(args):
    opts = parser.parse_args(args)
    with capture_errors(opts):
        COMMANDS[opts.command](opts)


if __name__ == "__main__":
    main(sys.argv[1:])
