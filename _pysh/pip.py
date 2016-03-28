from _pysh.config import get_deps
from _pysh.shell import shell_local
from _pysh.tasks import mark_task


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
            shell_local(opts, "pip install {deps}", deps=deps)
