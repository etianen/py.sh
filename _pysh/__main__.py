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


def format_shell(command, **kwargs):
    return command.format(**{
        key: quote(value) if isinstance(value, str) else " ".join(map(quote, value))
        for key, value
        in kwargs.items()
    })


def shell(opts, command, **kwargs):
    quoted_command = format_shell(command, **kwargs)
    process = subprocess.Popen(
        quoted_command,
        env=create_env(),
        executable=opts.shell,
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


def format_shell_local(opts, command, **kwargs):
    commands = []
    # Activate conda environment.
    commands.append(format_shell(
        "source {activate_script_path} {conda_env} &> /dev/null",
        activate_script_path=os.path.join(MINICONDA_BIN_PATH, "activate"),
        conda_env=opts.conda_env,
    ))
    # Activate local env file.
    env_file_path = os.path.join(PYSH_DIR_PATH, opts.env_file)
    if os.path.exists(env_file_path):
        commands.append(format_shell("source {env_file_path}", env_file_path=env_file_path))
    # Run the command.
    commands.append(format_shell(command, **kwargs))
    # All done!
    return " && ".join(commands)


def shell_local(opts, command, **kwargs):
    return shell(opts, format_shell_local(opts, command), **kwargs)


def shell_local_exec(opts, command, **kwargs):
    quoted_command = format_shell_local(opts, command, **kwargs)
    os.execve(opts.shell, [opts.shell, "-c", quoted_command], create_env())


# Conda.

def delete_conda_env(opts):
    with mark_task(opts, "Cleaning {} environment".format(opts.conda_env)):
        shell(opts, "conda env remove --yes --name {conda_env}", conda_env=opts.conda_env)


def reset_conda_env(opts, config):
    delete_conda_env(opts)
    # Create a new env.
    python_version = config.get("pysh").get("python").get("version", "3")
    with mark_task(opts, "Installing {} Python {}".format(opts.conda_env, python_version)):
        shell(
            opts,
            "conda create --yes --name {conda_env} python={python_version}",
            conda_env=opts.conda_env,
            python_version=python_version,
        )


def get_dependencies(opts, config, deps_key):
    deps_config = config.get("pysh").get(deps_key)
    return chain(
        deps_config.get("dependencies").items(),
        () if opts.production else deps_config.get("devDependencies").items(),
    )


def install_conda_deps(opts, config):
    deps = [
        "{}={}".format(*dep)
        for dep
        in get_dependencies(opts, config, "conda")
    ]
    if deps:
        with mark_task(opts, "Installing {} conda dependencies".format(opts.conda_env)):
            shell_local(opts, "conda install --yes {deps}", deps=deps)


# Pip.

def install_pip_deps(opts, config):
    deps = [
        "{}=={}".format(*dep)
        for dep
        in get_dependencies(opts, config, "pip")
    ]
    if deps:
        with mark_task(opts, "Installing {} pip dependencies".format(opts.conda_env)):
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
command_parsers = parser.add_subparsers(
    title="subcommands",
    help="The command to run.",
)


# Install.

def install(opts):
    config = load_config(opts)
    reset_conda_env(opts, config)
    install_conda_deps(opts, config)
    install_pip_deps(opts, config)
    run_install_scripts(opts, config)

install_parser = command_parsers.add_parser("install")
install_parser.add_argument(
    "--production",
    default=False,
    action="store_true",
    help="Don't install development dependencies.",
)
install_parser.set_defaults(func=install)


# Activate.

def activate(opts):
    config = load_config(opts)
    package_name = config.get("name", os.path.basename(PYSH_ROOT_PATH))
    with mark_task(opts, "Activating {} environment".format(opts.conda_env)):
        shell_local_exec(
            opts,
            """printf "done!
Deactivate environment with \'exit\' or [Ctl+D].
" && export PS1="({package_name}) \\h:\\W \\u\\$ " && bash""",
            package_name=package_name,
        )

activate_parser = command_parsers.add_parser("activate")
activate_parser.set_defaults(func=activate)


# Main method.

def main(args):
    opts = parser.parse_args(args)
    with capture_errors(opts):
        opts.func(opts)


if __name__ == "__main__":
    main(sys.argv[1:])
