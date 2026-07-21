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


def test_start_creates_icon_and_thread(mocker: pytest_mock.MockerFixture) -> None:
    service = _build_service()
    mock_icon = MagicMock()
    mock_thread = MagicMock()
    mocker.patch("chronobright.services.tray_service.pystray.Icon", return_value=mock_icon)
    mocker.patch(
        "chronobright.services.tray_service.threading.Thread",
        return_value=mock_thread,
    )

    service.start()

    mock_thread.start.assert_called_once()
    assert service._icon is mock_icon


def test_start_is_noop_when_thread_alive(mocker: pytest_mock.MockerFixture) -> None:
    service = _build_service()
    alive_thread = MagicMock()
    alive_thread.is_alive.return_value = True
    service._thread = alive_thread
    create_thread = mocker.patch("chronobright.services.tray_service.threading.Thread")

    service.start()

    create_thread.assert_not_called()


def test_stop_joins_thread_and_clears_state(mocker: pytest_mock.MockerFixture) -> None:
    service = _build_service()
    mock_icon = MagicMock()
    mock_thread = MagicMock()
    service._icon = mock_icon
    service._thread = mock_thread

    service.stop()

    mock_icon.stop.assert_called_once()
    mock_thread.join.assert_called_once_with(timeout=2.0)
    assert service._icon is None
    assert service._thread is None


def test_stop_is_noop_without_icon() -> None:
    service = _build_service()
    service.stop()
    assert service._icon is None


def test_show_hide_exit_callbacks_delegate(mocker: pytest_mock.MockerFixture) -> None:
    show = mocker.Mock()
    hide = mocker.Mock()
    exit_app = mocker.Mock()
    service = TrayService(
        on_show_window=show,
        on_hide_window=hide,
        on_exit_application=exit_app,
    )
    item = MagicMock()
    icon = MagicMock()

    service._show_window(icon, item)
    service._hide_window(icon, item)
    service._exit_application(icon, item)

    show.assert_called_once_with()
    hide.assert_called_once_with()
    exit_app.assert_called_once_with()


def test_update_menu_noop_without_icon() -> None:
    service = _build_service()
    service._update_menu()
