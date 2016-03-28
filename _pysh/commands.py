from functools import wraps
import os
import posixpath
import shutil
from _pysh.conda import delete_conda_env, reset_conda_env, install_conda_deps
from _pysh.config import load_config
from _pysh.pip import get_pip_deps, install_pip_deps
from _pysh.shell import shell, shell_local, shell_local_exec
from _pysh.tasks import TaskError, mark_task
from _pysh.utils import rimraf, mkdirp, download


PACKAGES_DIR = "packages"
CONDA_PACKAGES_DIR = os.path.join(PACKAGES_DIR, "conda")
PIP_PACKAGES_DIR = os.path.join(PACKAGES_DIR, "pip")


def prevent_unknown(func):
    @wraps(func)
    def do_prevent_unknown(opts, unknown_args):
        if unknown_args:
            raise TaskError("Unknown arguments: {}".format(" ".join(unknown_args)))
        return func(opts)
    return do_prevent_unknown


@prevent_unknown
def install(opts):
    config = load_config(opts)
    reset_conda_env(opts, config)
    install_conda_deps(opts, config)
    install_pip_deps(opts, config)
    # Run install scripts.
    with mark_task(opts, "Running install scripts"):
        for install_script in config.get("pysh").get("install", []):
            shell_local(opts, install_script)


@prevent_unknown
def dist(opts):
    config = load_config(opts)
    reset_conda_env(opts, config)
    try:
        install_conda_deps(opts, config)
        # Create a build environment.
        build_path = os.path.join(opts.root_path, opts.pysh_dir, "build")
        rimraf(build_path)
        mkdirp(build_path)
        try:
            build_pysh_path = os.path.join(build_path, opts.pysh_dir)
            # Copy source.
            with mark_task(opts, "Copying source"):
                shell(opts, "git archive HEAD | tar -x -C {build_path}", build_path=build_path)
            # Download offline conda packages.
            with mark_task(opts, "Downloading conda dependencies"):
                for dep_url in shell_local(opts, "conda list --explicit").decode().splitlines():
                    if not dep_url.startswith("#") and not dep_url.startswith("@"):
                        download(
                            dep_url,
                            os.path.join(build_pysh_path, CONDA_PACKAGES_DIR, posixpath.basename(dep_url)),
                        )
            # Download offline pip packages.
            with mark_task(opts, "Downloading pip packages"):
                shell_local(
                    opts,
                    "pip download --dest {dest_dir} {deps}",
                    dest_dir=os.path.join(build_pysh_path, PIP_PACKAGES_DIR),
                    deps=get_pip_deps(opts, config),
                )
            # Copy libs.
            build_lib_dir = os.path.join(build_pysh_path, opts.lib_dir)
            with mark_task(opts, "Copying libs"):
                shutil.copytree(os.path.join(opts.root_path, opts.pysh_dir, opts.lib_dir), build_lib_dir)
            # Compress the build.
            dist_file = os.path.join(opts.dist_dir, "{name}-{version}-{os_name}-amd64.zip".format(
                name=config.get("name", os.path.basename(opts.root_path)),
                version=config.get("version", "1.0.0"),
                os_name=opts.os_name,
            ))
            with mark_task(opts, "Creating archive {}".format(dist_file)):
                mkdirp(os.path.join(opts.root_path, opts.dist_dir))
                shell(
                    opts,
                    "cd {build_path} && zip -9 -qq -r {dist_path} './'",
                    build_path=build_path,
                    dist_path=os.path.join(opts.root_path, dist_file),
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
            """printf "done!
Deactivate environment with \'exit\' or [Ctl+D].
" && export PS1="({package_name}) \\h:\\W \\u\\$ " && bash""",
            package_name=package_name,
        )


def run(opts, unknown_args):
    shell_local_exec(
        opts,
        "{local_command} {unknown_args}",
        local_command=opts.local_command,
        unknown_args=unknown_args,
    )
