"""Confirm that project metadata is set correctly."""
import os
from typing import Any, Mapping

import toml

import philter_lite

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
PYPROJECT_TOML_PATH = os.path.join(TESTS_DIR, "..", "pyproject.toml")

pyproject_toml: Mapping[str, Any] = toml.load(PYPROJECT_TOML_PATH)


def test_version():
    """Ensure package version is reported correctly as metadata of the package itself.

    Manually asserted in the package __init__.py.
    """
    assert philter_lite.__version__ == pyproject_toml["tool"]["poetry"]["version"]
