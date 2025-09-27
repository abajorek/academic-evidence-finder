"""Tests for configuration loading utilities."""

from __future__ import annotations

import json
from importlib import util as importlib_util
from pathlib import Path

import pytest

from ae_finder import UnsupportedConfigFormatError, load_rules_config

def write_temp_file(tmp_path: Path, name: str, contents: str) -> Path:
    path = tmp_path / name
    path.write_text(contents, encoding="utf-8")
    return path


def test_load_rules_config_from_json(tmp_path: Path) -> None:
    payload = {"categories": {"Example": {"Any": {"any": ["pattern"]}}}}
    rules_path = write_temp_file(tmp_path, "rules.json", json.dumps(payload))

    loaded = load_rules_config(rules_path)

    assert loaded["categories"]["Example"]["Any"]["any"] == ["pattern"]


def test_load_rules_config_from_yaml_without_dependency(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    yaml_contents = "categories:\n  Example:\n    Any:\n      any:\n        - pattern\n"
    rules_path = write_temp_file(tmp_path, "rules.yml", yaml_contents)

    def fake_find_spec(name: str, package: str | None = None) -> None:
        if name == "yaml":
            return None
        return importlib_util.find_spec(name, package)

    monkeypatch.setattr("ae_finder.config_loader.find_spec", fake_find_spec)

    with pytest.raises(ModuleNotFoundError):
        load_rules_config(rules_path)


def test_load_rules_config_unsupported_extension(tmp_path: Path) -> None:
    config_path = write_temp_file(tmp_path, "rules.txt", "noop")

    with pytest.raises(UnsupportedConfigFormatError):
        load_rules_config(config_path)
