"""Configuration loading utilities for the Academic Evidence Finder."""

from __future__ import annotations

import json
from importlib.util import find_spec
from pathlib import Path
from typing import Any, Mapping


class UnsupportedConfigFormatError(RuntimeError):
    """Raised when a configuration file uses an unsupported format."""


def load_rules_config(path: str | Path) -> Mapping[str, Any]:
    """Load the rules configuration from JSON or YAML.

    JSON is preferred because it keeps the command-line tools free from external
    dependencies. YAML remains supported for backward compatibility when the
    optional :mod:`PyYAML` package is available. The loader produces a friendly
    error message when a YAML file is supplied but the dependency is missing.
    """

    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Configuration file not found: {path_obj}")

    suffix = path_obj.suffix.lower()
    text = path_obj.read_text(encoding="utf-8")

    if suffix == ".json":
        return json.loads(text)

    if suffix in {".yml", ".yaml"}:
        if find_spec("yaml") is None:
            raise ModuleNotFoundError(
                "PyYAML is required to read YAML configuration files. "
                "Install it with 'pip install PyYAML' or convert the file to JSON."
            )
        import yaml  # type: ignore[import-untyped]

        return yaml.safe_load(text)

    raise UnsupportedConfigFormatError(
        f"Unsupported configuration format: {path_obj.suffix or '(no extension)'}"
    )
