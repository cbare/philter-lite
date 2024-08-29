from importlib import resources
from typing import Any, MutableMapping

import toml

FILTERS_PATH = 'philter_lite.filters'


def load_conf_toml(package, filename):
    path = resources.files(package).joinpath(filename)
    with open(path, 'rt') as f:
        return toml.loads(f.read())


def load_regex_db() -> MutableMapping[str, Any]:
    return load_conf_toml(FILTERS_PATH, "regex.toml")


def load_regex_context_db() -> MutableMapping[str, Any]:
    return load_conf_toml(FILTERS_PATH, "regex_context.toml")


def load_set_db() -> MutableMapping[str, Any]:
    return load_conf_toml(FILTERS_PATH, "set.toml")
