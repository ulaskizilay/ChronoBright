"""Tests for :mod:`chronobright.time_utils`."""

from __future__ import annotations

from datetime import time

import pytest

from chronobright.time_utils import is_morning_period_active, normalize_time_string, parse_clock


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("8:0", "08:00"),
        ("08:00", "08:00"),
        ("9:5", "09:05"),
        (" 19:00 ", "19:00"),
    ],
)
def test_normalize_time_string_accepts_flexible_formats(raw: str, expected: str) -> None:
    assert normalize_time_string(raw) == expected


@pytest.mark.parametrize("raw", ["", "abc", "8", "8:60", "24:00", "08:0:0"])
def test_normalize_time_string_rejects_invalid_values(raw: str) -> None:
    with pytest.raises(ValueError, match="Invalid time format"):
        normalize_time_string(raw)


def test_parse_clock_returns_time_object() -> None:
    assert parse_clock("8:30") == time(8, 30)


def test_is_morning_period_active_for_standard_day_schedule() -> None:
    assert is_morning_period_active("08:00", "19:00", time(10, 0)) is True
    assert is_morning_period_active("08:00", "19:00", time(20, 0)) is False


def test_is_morning_period_active_for_overnight_schedule() -> None:
    assert is_morning_period_active("22:00", "06:00", time(23, 0)) is True
    assert is_morning_period_active("22:00", "06:00", time(3, 0)) is True
    assert is_morning_period_active("22:00", "06:00", time(12, 0)) is False
