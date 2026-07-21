"""Tests for :mod:`chronobright.config`."""

from __future__ import annotations

from pathlib import Path

import pytest

from chronobright.config import _resolve_base_dir, validate_brightness_level


def test_resolve_base_dir_uses_appdata(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("APPDATA", r"C:\Users\Test\AppData\Roaming")
    assert _resolve_base_dir() == Path(r"C:\Users\Test\AppData\Roaming")


def test_resolve_base_dir_falls_back_to_home(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPDATA", raising=False)
    result = _resolve_base_dir()
    assert result == Path.home() / "AppData" / "Roaming"


@pytest.mark.parametrize("level", [0, 50, 100])
def test_validate_brightness_level_accepts_valid_integers(level: int) -> None:
    validate_brightness_level(level)


@pytest.mark.parametrize("level", [True, False, -1, 101, 3.5, "50", None])
def test_validate_brightness_level_rejects_invalid_values(level: object) -> None:
    with pytest.raises(ValueError, match="Brightness must be an integer"):
        validate_brightness_level(level)
