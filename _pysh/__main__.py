"""
py.sh helpers.
"""

import argparse
from contextlib import contextmanager
from itertools import chain
import json
import os
from shlex import quote
import signal
import subprocess
import sys
import traceback


PYSH_OS_NAME = os.environ.pop("PYSH_OS_NAME")
PYSH_ROOT_PATH = os.environ.pop("PYSH_ROOT_PATH")
PYSH_SCRIPT = os.environ.pop("PYSH_SCRIPT")
PYSH_DIR = os.environ.pop("PYSH_DIR")
PYSH_MINICONDA_DIR = os.environ.pop("PYSH_MINICONDA_DIR")

PYSH_DIR_PATH = os.path.join(PYSH_ROOT_PATH, PYSH_DIR)
MINICONDA_DIR_PATH = os.path.join(PYSH_DIR_PATH, PYSH_MINICONDA_DIR)
MINICONDA_BIN_PATH = os.path.join(MINICONDA_DIR_PATH, "bin")


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


# Config.

class Config:

    def __init__(self, value, path):
        self._value = value
        self._path = []
        if not isinstance(value, dict):
            raise ValueError("Expected config data to be a dict.")

    def get(self, name, default={}):
        value = self._value.get(name, default)
        if value.__class__ != default.__class__:
            raise TaskError("Expected config {} to be a {}.".format(".".join(self._path, default.__class__.__name__)))
        if isinstance(value, dict):
            return Config(value, self._path + [name])
        return value

    def items(self):
        for key in self._value.keys():
            yield key, self.get(key, "")


def load_config(opts):
    with mark_task(opts, "Loading config from {}".format(opts.config_file)):
        package_json_path = os.path.join(PYSH_ROOT_PATH, opts.config_file)
        if os.path.exists(package_json_path):
            with open(package_json_path, "rb") as package_json_handle:
                try:
                    return Config(json.loads(package_json_handle.read().decode("utf-8")), [])
                except ValueError:
                    raise TaskError("Invalid {} config file.".format(opts.config_file))
        else:
            raise TaskWarning("Missing {} config file.".format(opts.config_file))
    # Provide a fallback config.
    return Config({}, [])


# Shell commands.

def create_env():
    env = os.environ.copy()
    env["PATH"] = "{}:{}".format(os.path.join(PYSH_DIR_PATH, PYSH_MINICONDA_DIR, "bin"), os.environ.get("PATH", ""))
    return env


def shell(command, **kwargs):
    # Escape the kwargs.
    quoted_kwargs = {
        key: quote(value) if isinstance(value, str) else " ".join(map(quote, value))
        for key, value
        in kwargs.items()
    }
    quoted_command = command.format(**quoted_kwargs)
    # Run the command.
    process = subprocess.Popen(
        quoted_command,
        env=create_env(),
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
        raise TaskError("{}\n{}{}".format(
            quoted_command,
            stdout.decode(errors="ignore"),
            stderr.decode(errors="ignore"),
        ))
    return stdout


def format_local_shell(opts, command):
    commands = ["source {} app".format(quote(os.path.join(MINICONDA_BIN_PATH, "activate")))]
    env_file_path = os.path.join(PYSH_DIR_PATH, opts.env_file)
    if os.path.exists(env_file_path):
        commands.append("source {}".format(quote(env_file_path)))
    commands.append(command)
    return " && ".join(commands)


def shell_local(opts, command, **kwargs):
    return shell(format_local_shell(opts, command), **kwargs)


# Conda.

def delete_conda_env(opts, env_name):
    with mark_task(opts, "Cleaning {} environment".format(env_name)):
        shell("conda env remove --yes --name {env_name}", env_name=env_name)


def reset_conda_env(opts, config, env_name):
    delete_conda_env(opts, env_name)
    # Create a new env.
    python_version = config.get("pysh").get("python").get("version", "3")
    with mark_task(opts, "Installing {} Python {}".format(env_name, python_version)):
        shell(
            "conda create --yes --name {env_name} python={python_version}",
            env_name=env_name,
            python_version=python_version,
        )


def get_dependencies(opts, config, deps_key):
    deps_config = config.get("pysh").get(deps_key)
    return chain(
        deps_config.get("dependencies").items(),
        () if opts.production else deps_config.get("devDependencies").items(),
    )


def install_conda_deps(opts, config, env_name):
    deps = [
        "{}={}".format(*dep)
        for dep
        in get_dependencies(opts, config, "conda")
    ]
    if deps:
        with mark_task(opts, "Installing {} conda dependencies".format(env_name)):
            shell_local(opts, "conda install --yes {deps}", deps=deps)


# Pip.

def install_pip_deps(opts, config, env_name):
    deps = [
        "{}=={}".format(*dep)
        for dep
        in get_dependencies(opts, config, "pip")
    ]
    if deps:
        with mark_task(opts, "Installing {} pip dependencies".format(env_name)):
            shell_local(opts, "pip install {deps}", deps=deps)


# Install scripts.

def run_install_scripts(opts, config):
    with mark_task(opts, "Running install scripts"):
        for install_script in config.get("pysh").get("install", []):
            shell_local(opts, install_script)


# Argparse.

parser = argparse.ArgumentParser(
    prog=PYSH_SCRIPT,
    description="Install and manage a standalone Python interpreter and environment.",
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
    "--traceback",
    default=False,
    action="store_true",
    help="Enable tracebacks in errors.",
)
command_parsers = parser.add_subparsers(
    title="subcommands",
    help="The command to run.",
)


# Install.

def install(opts):
    config = load_config(opts)
    reset_conda_env(opts, config, "app")
    install_conda_deps(opts, config, "app")
    install_pip_deps(opts, config, "app")
    run_install_scripts(opts, config)


install_parser = command_parsers.add_parser("install")
install_parser.add_argument(
    "--production",
    default=False,
    action="store_true",
    help="Don't install development dependencies.",
)
install_parser.set_defaults(func=install)


# Main method.

def main(args):
    opts = parser.parse_args(args)
    with capture_errors(opts):
        opts.func(opts)


if __name__ == "__main__":
    main(sys.argv[1:])
