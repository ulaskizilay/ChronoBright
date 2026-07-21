"""Shared fixtures for ChronoBright tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest

from chronobright.models import BrightnessScheduleConfig


@pytest.fixture
def sample_config() -> BrightnessScheduleConfig:
    return BrightnessScheduleConfig(
        morning_time="08:00",
        morning_brightness=90,
        evening_time="19:00",
        evening_brightness=80,
    )


@pytest.fixture
def config_path(tmp_path: Path) -> Path:
    return tmp_path / "config.json"


@pytest.fixture
def mock_sbc(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    mock = MagicMock()
    mock.get_brightness.return_value = [75]
    monkeypatch.setattr("chronobright.services.brightness_service.sbc", mock)
    return mock
