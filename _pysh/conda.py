import glob
import os
import posixpath
from _pysh.config import PACKAGES_DIR, BUILD_DIR, get_deps
from _pysh.shell import shell, shell_local
from _pysh.tasks import mark_task
from _pysh.utils import download


CONDA_PACKAGES_DIR = os.path.join(PACKAGES_DIR, "conda")


def delete_conda_env(opts):
    with mark_task(opts, "Cleaning {} environment".format(opts.conda_env)):
        shell(opts, "conda env remove --yes --name {conda_env}", conda_env=opts.conda_env)


def reset_conda_env(opts, config):
    delete_conda_env(opts)
    # Create a new env.
    if opts.offline:
        with mark_task(opts, "Installing {} conda dependencies".format(opts.conda_env)):
            deps = glob.glob(os.path.join(opts.root_path, opts.pysh_dir, CONDA_PACKAGES_DIR, "*.tar.bz2"))
            shell(
                opts,
                "conda create --offline --yes --name {conda_env} {deps}",
                conda_env=opts.conda_env,
                deps=deps,
            )
    else:
        with mark_task(opts, "Installing {} conda dependencies".format(opts.conda_env)):
            python_version = config.get("pysh").get("python").get("version", "3")
            deps = [
                "{}={}".format(*dep)
                for dep
                in get_deps(opts, config, "conda")
            ]
            shell(
                opts,
                "conda create --yes --name {conda_env} python={python_version} {deps}",
                conda_env=opts.conda_env,
                python_version=python_version,
                deps=deps,
            )


def download_conda_deps(opts):
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
                    os.path.join(
                        opts.root_path,
                        opts.pysh_dir,
                        BUILD_DIR,
                        opts.pysh_dir,
                        CONDA_PACKAGES_DIR,
                        posixpath.basename(dep),
                    ),
                )
