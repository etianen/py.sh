import glob
import os
from _pysh.config import get_deps
from _pysh.shell import format_shell, shell_local
from _pysh.tasks import mark_task
from _pysh.utils import rimraf, mkdirp


def get_pip_deps(opts, config):
    return [
        "{}=={}".format(*dep)
        for dep
        in get_deps(opts, config, "pip")
    ]


def get_pip_args(opts, config):
    pip_args = []
    # Handle extra index URLs.
    pip_args.append(" ".join(
        format_shell("--extra-index-url {index_url}", index_url=index_url)
        for index_url
        in config.get("pysh").get("pip").get("extra_index_urls", [])
    ))
    # All done!
    return " ".join(pip_args)


def install_pip_deps(opts, config):
    deps = get_pip_deps(opts, config)
    if deps:
        with mark_task(opts, "Installing {} pip dependencies".format(opts.conda_env)):
            shell_local(
                opts,
                "pip install {args} {{deps}}".format(args=get_pip_args(opts, config)),
                deps=deps,
            )


def install_pip_deps_offline(opts, config):
    deps = glob.glob(os.path.join(opts.pip_lib_path, "*.*"))
    if deps:
        with mark_task(opts, "Installing {} pip dependencies".format(opts.conda_env)):
            shell_local(
                opts,
                "pip install --no-index --no-deps {deps}",
                deps=deps,
            )


def download_pip_deps(opts, config):
    rimraf(opts.pip_lib_path)
    mkdirp(opts.pip_lib_path)
    deps = get_pip_deps(opts, config)
    if deps:
        with mark_task(opts, "Downloading pip dependencies"):
            shell_local(
                opts,
                "pip download {args} --dest {{dest_path}} {{deps}}".format(args=get_pip_args(opts, config)),
                dest_path=opts.pip_lib_path,
                deps=deps,
            )
