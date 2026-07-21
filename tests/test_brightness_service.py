"""Tests for :mod:`chronobright.services.brightness_service`."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from chronobright.services.brightness_service import BrightnessService


def test_get_all_brightness_returns_list(mock_sbc: MagicMock) -> None:
    mock_sbc.get_brightness.return_value = [60, 80]
    service = BrightnessService()
    assert service.get_all_brightness() == [60, 80]


def test_get_all_brightness_wraps_scalar(mock_sbc: MagicMock) -> None:
    mock_sbc.get_brightness.return_value = 55
    service = BrightnessService()
    assert service.get_all_brightness() == [55]


def test_get_all_brightness_returns_none_on_empty_list(mock_sbc: MagicMock) -> None:
    mock_sbc.get_brightness.return_value = []
    service = BrightnessService()
    assert service.get_all_brightness() is None


def test_get_all_brightness_returns_none_on_exception(mock_sbc: MagicMock) -> None:
    mock_sbc.get_brightness.side_effect = OSError("no display")
    service = BrightnessService()
    assert service.get_all_brightness() is None


def test_get_brightness_returns_first_display(mock_sbc: MagicMock) -> None:
    mock_sbc.get_brightness.return_value = [40, 70]
    service = BrightnessService()
    assert service.get_brightness() == 40


def test_get_brightness_returns_none_when_all_brightness_unavailable(mock_sbc: MagicMock) -> None:
    mock_sbc.get_brightness.side_effect = OSError("no display")
    service = BrightnessService()
    assert service.get_brightness() is None


def test_set_brightness_all_displays(mock_sbc: MagicMock) -> None:
    service = BrightnessService()
    service.set_brightness(75)
    mock_sbc.set_brightness.assert_called_once_with(75)


def test_set_brightness_single_display(mock_sbc: MagicMock) -> None:
    service = BrightnessService()
    service.set_brightness(75, display=1)
    mock_sbc.set_brightness.assert_called_once_with(75, display=1)


def test_set_brightness_rejects_invalid_level(mock_sbc: MagicMock) -> None:
    service = BrightnessService()
    with pytest.raises(ValueError):
        service.set_brightness(150)
    mock_sbc.set_brightness.assert_not_called()


def test_set_brightness_wraps_api_failure(mock_sbc: MagicMock) -> None:
    mock_sbc.set_brightness.side_effect = RuntimeError("driver error")
    service = BrightnessService()
    with pytest.raises(RuntimeError, match="Failed to set brightness"):
        service.set_brightness(50)
