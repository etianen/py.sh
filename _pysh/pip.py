import glob
import os
from _pysh.shell import shell_local
from _pysh.tasks import mark_task
from _pysh.utils import rimraf, mkdirp


def install_pip_deps_offline(opts):
    deps = glob.glob(os.path.join(opts.pip_lib_path, "*.*"))
    if deps:
        with mark_task(opts, "Installing {} pip dependencies".format(opts.conda_env)):
            shell_local(
                opts,
                "pip install {deps}",
                deps=deps,
            )


def download_pip_deps(opts):
    rimraf(opts.pip_lib_path)
    mkdirp(opts.pip_lib_path)
    deps = [
        dep
        for dep
        in shell_local(opts, "pip freeze").decode().splitlines()
    ]
    if deps:
        with mark_task(opts, "Downloading pip dependencies"):
            shell_local(
                opts,
                "pip download --dest {dest_path} {deps}",
                dest_path=opts.pip_lib_path,
                deps=deps,
            )
