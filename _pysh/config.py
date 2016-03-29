from itertools import chain
import json
import os
from _pysh.tasks import TaskError, TaskWarning, mark_task


class Config:

    def __init__(self, value, path):
        self._value = value
        self._path = []
        if not isinstance(value, dict):
            raise ValueError("Expected config data to be a dict.")

    def get(self, name, default={}):
        value = self._value.get(name, default)
        if value.__class__ != default.__class__:
            raise TaskError("Expected config {} to be a {}.".format(".".join(self._path, default.__class__.__name__)))
        if isinstance(value, dict):
            return Config(value, self._path + [name])
        return value

    def items(self):
        for key in self._value.keys():
            yield key, self.get(key, "")


def load_config(opts):
    with mark_task(opts, "Loading config from {}".format(opts.config_file)):
        package_json_path = os.path.join(opts.root_path, opts.config_file)
        if os.path.exists(package_json_path):
            with open(package_json_path, "rb") as package_json_handle:
                try:
                    return Config(json.loads(package_json_handle.read().decode("utf-8")), [])
                except ValueError:
                    raise TaskError("Invalid {} config file.".format(opts.config_file))
        else:
            raise TaskWarning("Missing {} config file.".format(opts.config_file))
    # Provide a fallback config.
    return Config({}, [])


def get_deps(opts, config, deps_key):
    deps_config = config.get("pysh").get(deps_key)
    return chain(
        deps_config.get("dependencies").items(),
        () if opts.production or opts.offline else deps_config.get("devDependencies").items(),
    )
