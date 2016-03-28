from _pysh.config import get_deps
from _pysh.shell import shell, shell_local
from _pysh.tasks import mark_task


def delete_conda_env(opts):
    with mark_task(opts, "Cleaning {} environment".format(opts.conda_env)):
        shell(opts, "conda env remove --yes --name {conda_env}", conda_env=opts.conda_env)


def reset_conda_env(opts, config):
    delete_conda_env(opts)
    # Create a new env.
    python_version = config.get("pysh").get("python").get("version", "3")
    with mark_task(opts, "Installing {} Python {}".format(opts.conda_env, python_version)):
        shell(
            opts,
            "conda create --yes --name {conda_env} python={python_version}",
            conda_env=opts.conda_env,
            python_version=python_version,
        )


def get_conda_deps(opts, config):
    return [
        "{}={}".format(*dep)
        for dep
        in get_deps(opts, config, "conda")
    ]


def install_conda_deps(opts, config):
    deps = get_conda_deps(opts, config)
    if deps:
        with mark_task(opts, "Installing {} conda dependencies".format(opts.conda_env)):
            shell_local(opts, "conda install --yes {deps}", deps=deps)
