import glob
import os
from _pysh.shell import format_shell, shell_local
from _pysh.tasks import mark_task
from _pysh.utils import rimraf, mkdirp


def get_pip_deps(opts):
    requirements_files = [os.path.join(opts.root_path, opts.requirements_file)]
    if not opts.production:
        requirements_files.append(os.path.join(opts.root_path, opts.requirements_dev_file))
    return " ".join(
        format_shell(
            "--requirement {requirements_file}",
            requirements_file=requirements_file,
        )
        for requirements_file
        in requirements_files
        if os.path.exists(requirements_file)
    )


def install_pip_deps(opts):
    deps = get_pip_deps(opts)
    if deps:
        with mark_task(opts, "Installing {} pip dependencies".format(opts.conda_env)):
            shell_local(opts, "pip install {deps}".format(deps=deps))


def install_pip_deps_offline(opts):
    deps = glob.glob(os.path.join(opts.lib_path, "pip", "*.*"))
    if deps:
        with mark_task(opts, "Installing {} pip dependencies".format(opts.conda_env)):
            shell_local(
                opts,
                "pip install {deps}",
                deps=deps,
            )


def download_pip_deps(opts):
    pip_lib_path = os.path.join(opts.build_lib_path, "pip")
    rimraf(pip_lib_path)
    mkdirp(pip_lib_path)
    deps = get_pip_deps(opts)
    if deps:
        with mark_task(opts, "Downloading pip dependencies"):
            shell_local(
                opts,
                "pip download --dest {{dest_path}} {deps}".format(deps=deps),
                dest_path=pip_lib_path,
            )
