from functools import wraps
import fnmatch
import os
import re
import shutil
import sys
import zipfile
from _pysh.conda import delete_conda_env, reset_conda_env, reset_conda_env_offline, download_conda_deps
from _pysh.pip import install_pip_deps, install_pip_deps_offline, download_pip_deps
from _pysh.shell import shell, shell_local_exec
from _pysh.styles import apply_styles
from _pysh.tasks import TaskError, mark_task
from _pysh.utils import rimraf, mkdirp


def prevent_unknown(func):
    @wraps(func)
    def do_prevent_unknown(opts, unknown_args):
        if unknown_args:
            raise TaskError("Unknown arguments: {}".format(" ".join(unknown_args)))
        return func(opts)
    return do_prevent_unknown


@prevent_unknown
def install(opts):
    if opts.offline:
        reset_conda_env_offline(opts)
        install_pip_deps_offline(opts)
    else:
        reset_conda_env(opts)
        install_pip_deps(opts)


@prevent_unknown
def dist(opts):
    reset_conda_env(opts)
    try:
        # Process the .pyshignore file.
        ignore_path = os.path.join(opts.root_path, opts.ignore_file)
        ignore_patterns = set([
            ".DS_Store",
            ".git",
            ".hg",
            ".svn",
            "CVS",
            "node_modules",
        ])
        if os.path.exists(ignore_path):
            with mark_task(opts, "Parsing ignore file"):
                with open(ignore_path, "rb") as ignore_handle:
                    for line in ignore_handle.read().decode("utf-8").splitlines():
                        line = line.strip()
                        if line and not line.startswith("#"):
                            ignore_patterns.add(line)
        ignore_patterns = list(map(re.compile, map(fnmatch.translate, ignore_patterns)))
        # Create the zipfile.
        mkdirp(os.path.dirname(output_path))
        rimraf(output_path)
        with zipfile.ZipFile(output_path, mode="w", compression=zipfile.ZIP_DEFLATED) as handle:
            # Copy source.
            with mark_task(opts, "Copying source"):
                for root, dirs, filenames in os.walk(opts.root_path):
                    for filename in filenames:
                        abs_filename = os.path.join(root, filename)
                        handle.write(abs_filename, os.path.relpath(abs_filename, opts.root_path))


        # Create a build environment.
        rimraf(opts.build_path)
        mkdirp(opts.build_path)
        try:
            # Copy source.
            with mark_task(opts, "Copying source"):
                shell(
                    opts,
                    "cd {root_path} && git archive HEAD --format=tar | tar -x -C {build_path}",
                    root_path=opts.root_path,
                    build_path=opts.build_path,
                )
            # Copy libs.
            with mark_task(opts, "Copying libs"):
                shutil.copytree(opts.lib_path, opts.build_lib_path)
            # Download deps.
            download_conda_deps(opts)
            download_pip_deps(opts)
            # Compress the build.
            output_path = os.path.join(opts.root_path, opts.output)
            with mark_task(opts, "Creating archive {}".format(opts.output)):



        finally:
            rimraf(opts.build_path)
    finally:
        delete_conda_env(opts)


@prevent_unknown
def activate(opts):
    with mark_task(opts, "Activating {} environment".format(opts.conda_env)):
        shell_local_exec(
            opts,
            apply_styles(opts, """printf "{success}done!{plain}
Deactivate environment with {code}exit{plain} or {code}[Ctl+D]{plain}.
" && export PS1="(\[{code}\]{{dirname}}\[{plain}\]) \\h:\\W \\u\\$ " && bash"""),
            dirname=os.path.basename(opts.root_path),
        )


def run(opts, unknown_args):
    shell_local_exec(
        opts,
        "{unknown_args}",
        unknown_args=unknown_args,
    )


@prevent_unknown
def welcome(opts):
    sys.stdout.write(apply_styles(opts, r'''{success}                   _
{success}                  | |
{success} _ __  _   _   ___| |__
{success}| '_ \| | | | / __| '_ \
{success}| |_) | |_| |_\__ \ | | |
{success}| .__/ \__, (_)___/_| |_|
{success}| |     __/ |
{success}|_|    |___/

{success}py.sh{plain} is now installed!

A standalone Python interpreter has been installed into {code}{{work_dir}}{plain}.
{success}Recommended:{plain} Add {code}{{work_dir}}{plain} to your {code}.gitignore{plain} file.

Use {code}./{{script_name}}{plain} to manage your environment.
{success}Hint:{plain} You can learn a lot from {code}./{{script_name}} --help{plain}
and {code}./{{script_name}} <command name> --help{plain}.

''').format(
        work_dir=os.path.relpath(opts.work_path, opts.root_path),
        script_name=opts.script_name,
    ))
