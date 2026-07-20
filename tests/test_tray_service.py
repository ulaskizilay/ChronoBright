"""Smoke tests for :class:`TrayService`.

These cover the pure, side-effect-free surface (icon image generation and the
window-visibility state machine) without instantiating the actual pystray icon,
which would require a running display backend unsuitable for CI.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest_mock
from PIL import Image

from chronobright.services.tray_service import TrayService


def _build_service() -> TrayService:
    return TrayService(
        on_show_window=lambda: None,
        on_hide_window=lambda: None,
        on_exit_application=lambda: None,
    )


def test_create_icon_image_returns_rgb_image_of_expected_size() -> None:
    image = TrayService._create_icon_image()

    assert isinstance(image, Image.Image)
    assert image.size == (64, 64)
    assert image.mode == "RGB"


def test_new_service_defaults_to_window_visible() -> None:
    service = _build_service()

    assert service._window_visible is True


def test_set_window_visible_updates_state_and_calls_update_menu(
    mocker: pytest_mock.MockerFixture,
) -> None:
    service = _build_service()
    service._icon = MagicMock()
    update_menu = mocker.patch.object(service, "_update_menu")

    service.set_window_visible(False)

    assert service._window_visible is False
    update_menu.assert_called_once_with()

    service.set_window_visible(True)

    assert service._window_visible is True
    assert update_menu.call_count == 2


def test_can_show_and_can_hide_window_reflect_visibility_state() -> None:
    service = _build_service()
    item = MagicMock()

    service._window_visible = True
    assert service._can_show_window(item) is False
    assert service._can_hide_window(item) is True

    service._window_visible = False
    assert service._can_show_window(item) is True
    assert service._can_hide_window(item) is False
