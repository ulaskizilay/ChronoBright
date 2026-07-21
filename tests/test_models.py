"""Tests for :mod:`chronobright.models`."""

from __future__ import annotations

import pytest

from chronobright.models import BrightnessScheduleConfig


def test_valid_config_passes_validation() -> None:
    cfg = BrightnessScheduleConfig(
        morning_time="08:00",
        morning_brightness=90,
        evening_time="19:00",
        evening_brightness=80,
    )
    cfg.validate()


def test_post_init_rejects_invalid_time() -> None:
    with pytest.raises(ValueError, match="Invalid time format"):
        BrightnessScheduleConfig(
            morning_time="not-a-time",
            morning_brightness=90,
            evening_time="19:00",
            evening_brightness=80,
        )


def test_post_init_rejects_invalid_brightness() -> None:
    with pytest.raises(ValueError, match="Brightness must be an integer"):
        BrightnessScheduleConfig(
            morning_time="08:00",
            morning_brightness=101,
            evening_time="19:00",
            evening_brightness=80,
        )


def test_post_init_rejects_bool_brightness() -> None:
    with pytest.raises(ValueError, match="Brightness must be an integer"):
        BrightnessScheduleConfig(
            morning_time="08:00",
            morning_brightness=True,  # type: ignore[arg-type]
            evening_time="19:00",
            evening_brightness=80,
        )


def test_post_init_rejects_equal_morning_and_evening_times() -> None:
    with pytest.raises(ValueError, match="Morning and evening times must be different"):
        BrightnessScheduleConfig(
            morning_time="08:00",
            morning_brightness=90,
            evening_time="08:00",
            evening_brightness=80,
        )


def test_post_init_normalizes_flexible_time_formats() -> None:
    cfg = BrightnessScheduleConfig(
        morning_time="8:0",
        morning_brightness=90,
        evening_time="19:0",
        evening_brightness=80,
    )
    assert cfg.morning_time == "08:00"
    assert cfg.evening_time == "19:00"


def test_validate_time_reraises_value_error_with_context() -> None:
    with pytest.raises(ValueError, match="Invalid time format: 99:99"):
        BrightnessScheduleConfig._validate_time("99:99")


def test_validate_time_rejects_non_string() -> None:
    with pytest.raises(ValueError, match="Invalid time format"):
        BrightnessScheduleConfig._validate_time(123)  # type: ignore[arg-type]
