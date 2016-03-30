import os
from _pysh.config import get_deps
from _pysh.constants import PACKAGES_DIR, BUILD_DIR
from _pysh.shell import format_shell, shell_local
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
                # Handle extra index URLs.
                index_urls = " ".join(
                    format_shell("--extra-index-url {index_url}", index_url=index_url)
                    for index_url
                    in config.get("pysh").get("pip").get("index_urls", [])
                )
                # Run the install.
                shell_local(opts, "pip install {index_urls} {{deps}}".format(index_urls=index_urls), deps=deps)


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
