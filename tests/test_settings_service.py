"""Tests for :mod:`chronobright.services.settings_service`."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from chronobright.models import BrightnessScheduleConfig
from chronobright.services.settings_service import SettingsService


@pytest.fixture
def service(config_path: Path) -> SettingsService:
    return SettingsService(config_path=config_path)


def test_load_schedule_missing_file_returns_defaults(service: SettingsService) -> None:
    result = service.load_schedule()
    assert result.source == "missing"
    assert result.config.morning_time == "08:00"
    assert result.config.evening_brightness == 80


def test_save_and_load_round_trip(service: SettingsService, sample_config: BrightnessScheduleConfig) -> None:
    service.save_schedule(sample_config)
    result = service.load_schedule()
    assert result.source == "saved"
    assert result.config == sample_config


def test_save_and_load_preserves_language(service: SettingsService, sample_config: BrightnessScheduleConfig) -> None:
    service.save_schedule(sample_config, language="tr")

    assert service.load_schedule().language == "tr"


def test_load_schedule_defaults_invalid_language_to_english(
    service: SettingsService, config_path: Path
) -> None:
    config_path.write_text(
        json.dumps(
            {
                "morning_time": "08:00",
                "morning_brightness": 90,
                "evening_time": "19:00",
                "evening_brightness": 80,
                "language": "unsupported",
            }
        ),
        encoding="utf-8",
    )

    assert service.load_schedule().language == "en"


def test_load_schedule_corrupt_json_returns_fallback(service: SettingsService, config_path: Path) -> None:
    config_path.write_text("{not valid json", encoding="utf-8")
    result = service.load_schedule()
    assert result.source == "fallback"


def test_load_schedule_missing_key_returns_fallback(service: SettingsService, config_path: Path) -> None:
    config_path.write_text(json.dumps({"morning_time": "08:00"}), encoding="utf-8")
    result = service.load_schedule()
    assert result.source == "fallback"


def test_load_schedule_rejects_bool_brightness(service: SettingsService, config_path: Path) -> None:
    config_path.write_text(
        json.dumps(
            {
                "morning_time": "08:00",
                "morning_brightness": True,
                "evening_time": "19:00",
                "evening_brightness": 80,
            }
        ),
        encoding="utf-8",
    )
    result = service.load_schedule()
    assert result.source == "fallback"


def test_load_schedule_rejects_equal_times(service: SettingsService, config_path: Path) -> None:
    config_path.write_text(
        json.dumps(
            {
                "morning_time": "08:00",
                "morning_brightness": 90,
                "evening_time": "08:00",
                "evening_brightness": 80,
            }
        ),
        encoding="utf-8",
    )
    result = service.load_schedule()
    assert result.source == "fallback"


def test_save_schedule_atomic_write(service: SettingsService, sample_config: BrightnessScheduleConfig, config_path: Path) -> None:
    service.save_schedule(sample_config)
    assert config_path.exists()
    assert not config_path.with_suffix(".json.tmp").exists()
    payload = json.loads(config_path.read_text(encoding="utf-8"))
    assert payload["morning_brightness"] == 90
