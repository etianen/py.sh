import os
from _pysh.config import get_deps
from _pysh.constants import PACKAGES_DIR, BUILD_DIR
from _pysh.shell import shell_local
from _pysh.tasks import mark_task


PIP_PACKAGES_DIR = os.path.join(PACKAGES_DIR, "pip")


def get_pip_deps(opts, config):
    return [
        "{}=={}".format(*dep)
        for dep
        in get_deps(opts, config, "pip")
    ]


def install_pip_deps(opts, config):
    deps = get_pip_deps(opts, config)
    if deps:
        with mark_task(opts, "Installing {} pip dependencies".format(opts.conda_env)):
            if opts.offline:
                shell_local(
                    opts,
                    "pip install --no-index --find-links {packages_dir} {deps}",
                    packages_dir=os.path.join(opts.work_path, PIP_PACKAGES_DIR),
                    deps=deps,
                )
            else:
                shell_local(opts, "pip install {deps}", deps=deps)


def download_pip_deps(opts, config):
    deps = get_pip_deps(opts, config)
    if deps:
        with mark_task(opts, "Downloading pip dependencies"):
            shell_local(
                opts,
                "pip download --dest {dest_dir} {deps}",
                dest_dir=os.path.join(opts.work_path, BUILD_DIR, opts.work_dir, PIP_PACKAGES_DIR),
                deps=deps,
            )
