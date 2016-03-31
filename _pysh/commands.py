from functools import wraps
import os
import shutil
from _pysh.conda import delete_conda_env, reset_conda_env, reset_conda_env_offline, download_conda_deps
from _pysh.config import load_config
from _pysh.pip import install_pip_deps, install_pip_deps_offline, download_pip_deps
from _pysh.shell import shell, shell_local, shell_local_exec
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
def clean(opts):
    with mark_task(opts, "Cleaning"):
        rimraf(opts.work_path)


@prevent_unknown
def install(opts):
    config = load_config(opts)
    if opts.offline:
        reset_conda_env_offline(opts, config)
        install_pip_deps_offline(opts, config)
    else:
        reset_conda_env(opts, config)
        install_pip_deps(opts, config)
    # Run install scripts.
    install_scripts = config.get("pysh").get("install", [])
    if install_scripts:
        with mark_task(opts, "Running install scripts"):
            for install_script in install_scripts:
                shell_local(opts, install_script)


@prevent_unknown
def download_deps(opts):
    config = load_config(opts)
    download_conda_deps(opts)
    download_pip_deps(opts, config)


@prevent_unknown
def dist(opts):
    config = load_config(opts)
    reset_conda_env(opts, config)
    try:
        # Create a build environment.
        build_path = os.path.join(opts.work_path, "build")
        rimraf(build_path)
        mkdirp(build_path)
        try:
            # Copy source.
            with mark_task(opts, "Copying source"):
                shell(
                    opts,
                    "cd {root_path} && git archive HEAD --format=tar | tar -x -C {build_path}",
                    root_path=opts.root_path,
                    build_path=build_path,
                )
            # Download deps.
            download_conda_deps(opts)
            download_pip_deps(opts, config)
            # Copy libs.
            with mark_task(opts, "Copying libs"):
                shutil.copytree(
                    opts.lib_path,
                    os.path.join(build_path, os.path.relpath(opts.lib_path, opts.root_path)),
                )
            # Compress the build.
            dist_path = os.path.join(opts.root_path, opts.dist_dir)
            mkdirp(dist_path)
            dist_file = os.path.join("{name}-{version}-{os_name}-amd64.zip".format(
                name=config.get("name", os.path.basename(opts.root_path)),
                version=config.get("version", "1.0.0"),
                os_name=opts.os_name,
            ))
            with mark_task(opts, "Creating archive {}".format(dist_file)):
                dist_file_path = os.path.join(dist_path, dist_file)
                rimraf(dist_file_path)
                shell(
                    opts,
                    "cd {build_path} && zip -9 -qq -r {dist_file_path} './'",
                    build_path=build_path,
                    dist_file_path=dist_file_path,
                )
        finally:
            rimraf(build_path)
    finally:
        delete_conda_env(opts)


@prevent_unknown
def activate(opts):
    config = load_config(opts)
    package_name = config.get("name", os.path.basename(opts.root_path))
    with mark_task(opts, "Activating {} environment".format(opts.conda_env)):
        shell_local_exec(
            opts,
            apply_styles(opts, """printf "{success}done!{plain}
Deactivate environment with {code}exit{plain} or {code}[Ctl+D]{plain}.
" && export PS1="({code}{{package_name}}{plain}) \\h:\\W \\u\\$ " && bash"""),
            package_name=package_name,
        )


def run(opts, unknown_args):
    shell_local_exec(
        opts,
        "{unknown_args}",
        unknown_args=unknown_args,
    )
