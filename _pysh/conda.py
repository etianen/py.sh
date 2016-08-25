import glob
import os
import posixpath
from _pysh.shell import format_shell, shell, shell_local
from _pysh.tasks import mark_task
from _pysh.utils import rimraf, mkdirp, download


def delete_conda_env(opts):
    with mark_task(opts, "Cleaning {} environment".format(opts.conda_env)):
        shell(opts, "conda remove --yes --offline --name {conda_env} --all", conda_env=opts.conda_env)


def reset_conda_env(opts):
    delete_conda_env(opts)
    # Update conda.
    with mark_task(opts, "Updating conda"):
        shell(opts, "conda update conda --yes")
    # Create a new env.
    with mark_task(opts, "Installing {} conda dependencies".format(opts.conda_env)):
        requirements_files = [os.path.join(opts.root_path, opts.requirements_conda_file)]
        if not opts.production:
            requirements_files.append(os.path.join(opts.root_path, opts.requirements_conda_dev_file))
        deps = " ".join(
            format_shell(
                "--file {requirements_file}",
                requirements_file=requirements_file,
            )
            for requirements_file
            in requirements_files
            if os.path.exists(requirements_file)
        ) or "python"
        shell(
            opts,
            "conda create --yes --name {{conda_env}} {deps}".format(deps=deps),
            conda_env=opts.conda_env,
        )


def reset_conda_env_offline(opts):
    delete_conda_env(opts)
    # Create a new env.
    with mark_task(opts, "Installing {} conda dependencies".format(opts.conda_env)):
        deps = glob.glob(os.path.join(opts.lib_path, "conda", "*.tar.bz2"))
        shell(
            opts,
            "conda create --yes --offline --name {conda_env} {deps}",
            conda_env=opts.conda_env,
            deps=deps,
        )


def download_conda_deps(opts):
    conda_lib_path = os.path.join(opts.build_lib_path, "conda")
    rimraf(conda_lib_path)
    mkdirp(conda_lib_path)
    deps = [
        dep
        for dep
        in shell_local(opts, "conda list --explicit").decode().splitlines()
        if not dep.startswith("#") and not dep.startswith("@")
    ]
    if deps:
        with mark_task(opts, "Downloading conda dependencies"):
            for dep in deps:
                download(
                    dep,
                    os.path.join(conda_lib_path, posixpath.basename(dep)),
                )
