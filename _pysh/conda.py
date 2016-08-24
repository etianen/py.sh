import glob
import os
import posixpath
from _pysh.shell import shell, shell_local
from _pysh.tasks import TaskError, mark_task
from _pysh.utils import rimraf, mkdirp, download


def delete_conda_env(opts):
    with mark_task(opts, "Cleaning {} environment".format(opts.conda_env)):
        shell(opts, "conda remove --yes --name {conda_env} --all --offline", conda_env=opts.conda_env)


def reset_conda_env(opts):
    delete_conda_env(opts)
    # Update conda.
    with mark_task(opts, "Updating conda"):
        shell(opts, "conda update conda conda-env --yes")
    # Create a new env.
    with mark_task(opts, "Installing {} conda dependencies".format(opts.conda_env)):
        environment_file = os.path.join(opts.root_path, opts.environment_file)
        if not os.path.exists(environment_file):
            raise TaskError("Missing {}".format(opts.environment_file))
        shell(
            opts,
            "conda env create --name {conda_env} --file {environment_file}",
            conda_env=opts.conda_env,
            environment_file=environment_file,
        )


def reset_conda_env_offline(opts):
    delete_conda_env(opts)
    # Create a new env.
    with mark_task(opts, "Installing {} conda dependencies".format(opts.conda_env)):
        deps = glob.glob(os.path.join(opts.conda_lib_path, "*.tar.bz2"))
        shell(
            opts,
            "conda create --offline --yes --name {conda_env} {deps}",
            conda_env=opts.conda_env,
            deps=deps,
        )


def download_conda_deps(opts):
    rimraf(opts.conda_lib_path)
    mkdirp(opts.conda_lib_path)
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
                    os.path.join(opts.conda_lib_path, posixpath.basename(dep)),
                )
