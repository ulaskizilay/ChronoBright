"""Tests for :class:`chronobright.ui.app.ChronoBrightApp` with mocked GUI dependencies."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from chronobright.i18n import Translator
from chronobright.models import BrightnessScheduleConfig
from chronobright.services.settings_service import SettingsLoadResult


@pytest.fixture
def app_instance():
    """Build a ChronoBrightApp instance without running real GUI initialisation."""
    with (
        patch("chronobright.ui.app.apply_theme"),
        patch("chronobright.ui.app.ctk.CTk.__init__", return_value=None),
        patch("chronobright.ui.app.BrightnessService") as mock_brightness_cls,
        patch("chronobright.ui.app.SettingsService") as mock_settings_cls,
        patch("chronobright.ui.app.ScheduleService") as mock_schedule_cls,
        patch("chronobright.ui.app.TrayService") as mock_tray_cls,
    ):
        from chronobright.ui.app import ChronoBrightApp

        app = ChronoBrightApp.__new__(ChronoBrightApp)
        app._is_exiting = False
        app._window_in_tray = False
        app._startup_brightness = [70, 80]

        app._brightness_service = mock_brightness_cls.return_value
        app._brightness_service.get_all_brightness.return_value = [70, 80]

        app._settings_service = mock_settings_cls.return_value
        app._schedule_service = mock_schedule_cls.return_value
        app._tray_service = mock_tray_cls.return_value
        app._translator = Translator()
        app._current_schedule_config = BrightnessScheduleConfig(
            morning_time="08:00",
            morning_brightness=90,
            evening_time="19:00",
            evening_brightness=80,
        )
        app._status_key = "idle"
        app._status_values = {}
        app._status_color = "gray"

        app._entry_morning_time = MagicMock()
        app._entry_evening_time = MagicMock()
        app._slider_morning = MagicMock()
        app._slider_evening = MagicMock()
        app._lbl_status = MagicMock()
        app._lbl_morning_value = MagicMock()
        app._lbl_evening_value = MagicMock()

        app.after = MagicMock()
        app.withdraw = MagicMock()
        app.deiconify = MagicMock()
        app.lift = MagicMock()
        app.focus_force = MagicMock()
        app.destroy = MagicMock()
        app.winfo_viewable = MagicMock(return_value=True)
        app.title = MagicMock()
        app.geometry = MagicMock()
        app.resizable = MagicMock()
        app.protocol = MagicMock()
        app.grid_columnconfigure = MagicMock()
        app.grid_rowconfigure = MagicMock()

        yield app


def test_read_form_config_reads_entries(app_instance) -> None:
    app_instance._entry_morning_time.get.return_value = "08:00"
    app_instance._entry_evening_time.get.return_value = "19:00"
    app_instance._slider_morning.get.return_value = 90.0
    app_instance._slider_evening.get.return_value = 80.0

    config = app_instance._read_form_config()

    assert config.morning_time == "08:00"
    assert config.morning_brightness == 90
    assert config.evening_time == "19:00"
    assert config.evening_brightness == 80


def test_read_form_config_normalizes_flexible_time(app_instance) -> None:
    app_instance._entry_morning_time.get.return_value = "8:0"
    app_instance._entry_evening_time.get.return_value = "19:0"
    app_instance._slider_morning.get.return_value = 90.0
    app_instance._slider_evening.get.return_value = 80.0

    config = app_instance._read_form_config()

    assert config.morning_time == "08:00"
    assert config.evening_time == "19:00"


def test_read_form_config_rejects_invalid_time(app_instance) -> None:
    app_instance._entry_morning_time.get.return_value = ""
    app_instance._entry_evening_time.get.return_value = "19:00"
    app_instance._slider_morning.get.return_value = 90.0
    app_instance._slider_evening.get.return_value = 80.0

    with pytest.raises(ValueError, match="Invalid time format"):
        app_instance._read_form_config()


def test_apply_brightness_sets_level_and_status(app_instance) -> None:
    app_instance._apply_brightness(85, "Morning")

    app_instance._brightness_service.set_brightness.assert_called_once_with(85)
    app_instance.after.assert_called_once()


def test_apply_brightness_handles_runtime_error(app_instance) -> None:
    app_instance._brightness_service.set_brightness.side_effect = RuntimeError("failed")

    app_instance._apply_brightness(85, "Morning")

    app_instance.after.assert_called_once()


def test_on_apply_clicked_saves_and_applies(app_instance) -> None:
    config = BrightnessScheduleConfig(
        morning_time="08:00",
        morning_brightness=90,
        evening_time="19:00",
        evening_brightness=80,
    )
    app_instance._read_form_config = MagicMock(return_value=config)
    app_instance._schedule_service.apply_schedule.return_value = "Schedule active"

    app_instance._on_apply_clicked()

    app_instance._settings_service.save_schedule.assert_called_once_with(config, "en")
    app_instance._schedule_service.apply_schedule.assert_called_once_with(config)


def test_on_apply_clicked_shows_validation_error(app_instance) -> None:
    with patch.object(app_instance, "_read_form_config", side_effect=ValueError("bad input")):
        app_instance._on_apply_clicked()

    app_instance._settings_service.save_schedule.assert_not_called()


def test_load_saved_schedule_applies_when_source_saved(app_instance) -> None:
    config = BrightnessScheduleConfig(
        morning_time="08:00",
        morning_brightness=90,
        evening_time="19:00",
        evening_brightness=80,
    )
    app_instance._settings_service.load_schedule.return_value = SettingsLoadResult(
        config=config,
        source="saved",
    )
    app_instance._schedule_service.apply_schedule.return_value = "Schedule active"
    app_instance._populate_form = MagicMock()

    app_instance._load_saved_schedule()

    app_instance._populate_form.assert_called_once_with(config)
    app_instance._schedule_service.apply_schedule.assert_called_once_with(config)


def test_load_saved_schedule_shows_fallback_message(app_instance) -> None:
    config = BrightnessScheduleConfig(
        morning_time="08:00",
        morning_brightness=90,
        evening_time="19:00",
        evening_brightness=80,
    )
    app_instance._settings_service.load_schedule.return_value = SettingsLoadResult(
        config=config,
        source="fallback",
    )
    app_instance._populate_form = MagicMock()

    app_instance._load_saved_schedule()

    app_instance._lbl_status.configure.assert_called()


def test_hide_window_to_tray_withdraws_when_viewable(app_instance) -> None:
    app_instance.hide_window_to_tray()

    app_instance.withdraw.assert_called_once()
    app_instance._tray_service.set_window_visible.assert_called_once_with(False)


def test_hide_window_to_tray_skips_when_already_in_tray(app_instance) -> None:
    app_instance._window_in_tray = True

    app_instance.hide_window_to_tray()

    app_instance.withdraw.assert_not_called()


def test_show_window_restores_from_tray(app_instance) -> None:
    app_instance.show_window()

    app_instance.deiconify.assert_called_once()
    app_instance._tray_service.set_window_visible.assert_called_once_with(True)


def test_exit_application_stops_services_and_restores(app_instance) -> None:
    app_instance.exit_application()

    app_instance._tray_service.stop.assert_called_once()
    app_instance._schedule_service.stop.assert_called_once()
    assert app_instance._brightness_service.set_brightness.call_count == 2
    app_instance.destroy.assert_called_once()


def test_exit_application_is_idempotent(app_instance) -> None:
    app_instance._is_exiting = True

    app_instance.exit_application()

    app_instance._tray_service.stop.assert_not_called()


def test_restore_startup_brightness_skips_when_unavailable(app_instance) -> None:
    app_instance._startup_brightness = None

    app_instance._restore_startup_brightness()

    app_instance._brightness_service.set_brightness.assert_not_called()


def test_restore_startup_brightness_single_display(app_instance) -> None:
    app_instance._startup_brightness = [65]

    app_instance._restore_startup_brightness()

    app_instance._brightness_service.set_brightness.assert_called_once_with(65)


def test_tray_callbacks_schedule_on_main_thread(app_instance) -> None:
    app_instance._show_window_from_tray()
    app_instance._hide_window_from_tray()
    app_instance._exit_from_tray()

    assert app_instance.after.call_count == 3


def test_on_apply_clicked_handles_oserror(app_instance) -> None:
    config = BrightnessScheduleConfig(
        morning_time="08:00",
        morning_brightness=90,
        evening_time="19:00",
        evening_brightness=80,
    )
    with patch.object(app_instance, "_read_form_config", return_value=config):
        app_instance._settings_service.save_schedule.side_effect = OSError("disk full")
        app_instance._on_apply_clicked()

    app_instance._schedule_service.apply_schedule.assert_not_called()


def test_on_morning_and_evening_slider_updates_labels(app_instance) -> None:
    app_instance._on_morning_slider_moved(42.0)
    app_instance._on_evening_slider_moved(33.0)

    app_instance._lbl_morning_value.configure.assert_called_with(text="Brightness: 42%")
    app_instance._lbl_evening_value.configure.assert_called_with(text="Brightness: 33%")


def test_status_is_retranslated_when_language_changes(app_instance) -> None:
    app_instance._translator.set_language("tr")

    app_instance._set_status("brightness_applied", "blue", level=85, period_key="morning")

    app_instance._lbl_status.configure.assert_called_with(
        text="Durum: %85 olarak ayarlandı (Sabah)", text_color="blue"
    )


def test_language_change_persists_preference_and_refreshes_ui(app_instance) -> None:
    app_instance._language_label = MagicMock()
    app_instance._header_label = MagicMock()
    app_instance._morning_heading = MagicMock()
    app_instance._evening_heading = MagicMock()
    app_instance._btn_apply = MagicMock()
    app_instance._btn_exit = MagicMock()
    app_instance._slider_morning.get.return_value = 90
    app_instance._slider_evening.get.return_value = 80

    app_instance._on_language_changed("Türkçe")

    assert app_instance._translator.language == "tr"
    app_instance._settings_service.save_schedule.assert_called_once_with(
        app_instance._current_schedule_config, "tr"
    )
    app_instance._tray_service.refresh_menu_text.assert_called_once_with()


def test_populate_form_sets_entries_and_sliders(app_instance) -> None:
    config = BrightnessScheduleConfig(
        morning_time="07:30",
        morning_brightness=85,
        evening_time="20:30",
        evening_brightness=65,
    )

    app_instance._populate_form(config)

    app_instance._entry_morning_time.delete.assert_called_once()
    app_instance._entry_morning_time.insert.assert_called()
    app_instance._slider_morning.set.assert_called_once_with(85)


def test_load_saved_schedule_shows_missing_message(app_instance) -> None:
    config = BrightnessScheduleConfig(
        morning_time="08:00",
        morning_brightness=90,
        evening_time="19:00",
        evening_brightness=80,
    )
    app_instance._settings_service.load_schedule.return_value = SettingsLoadResult(
        config=config,
        source="missing",
    )
    app_instance._populate_form = MagicMock()

    app_instance._load_saved_schedule()

    app_instance._lbl_status.configure.assert_called()


def test_on_window_close_hides_to_tray(app_instance) -> None:
    with patch.object(app_instance, "hide_window_to_tray") as hide:
        app_instance._on_window_close()
    hide.assert_called_once()


def test_show_window_skips_when_exiting(app_instance) -> None:
    app_instance._is_exiting = True
    app_instance.show_window()
    app_instance.deiconify.assert_not_called()


def test_hide_window_skips_when_exiting(app_instance) -> None:
    app_instance._is_exiting = True
    app_instance.hide_window_to_tray()
    app_instance.withdraw.assert_not_called()


def test_restore_startup_brightness_logs_failure(app_instance) -> None:
    app_instance._startup_brightness = [65]
    app_instance._brightness_service.set_brightness.side_effect = RuntimeError("failed")

    app_instance._restore_startup_brightness()


def test_build_layout_wires_panels() -> None:
    import chronobright.ui.app as app_module
    from chronobright.ui.app import ChronoBrightApp

    app = MagicMock(spec=[])
    app.grid_columnconfigure = MagicMock()
    app.grid_rowconfigure = MagicMock()
    app._on_morning_slider_moved = MagicMock()
    app._on_evening_slider_moved = MagicMock()
    app._on_apply_clicked = MagicMock()
    app._on_language_changed = MagicMock()
    app._translate = MagicMock(side_effect=lambda key, **_values: key)
    app._translator = Translator()
    app._format_status = ChronoBrightApp._format_status.__get__(app, ChronoBrightApp)
    app._set_status = ChronoBrightApp._set_status.__get__(app, ChronoBrightApp)
    app.exit_application = MagicMock()
    app._build_morning_panel = ChronoBrightApp._build_morning_panel.__get__(app, ChronoBrightApp)
    app._build_evening_panel = ChronoBrightApp._build_evening_panel.__get__(app, ChronoBrightApp)

    label = MagicMock()
    button = MagicMock()
    frame = MagicMock()
    entry = MagicMock()
    slider = MagicMock()
    option_menu = MagicMock()
    with (
        patch.object(app_module.ctk, "CTkFont", return_value=MagicMock()),
        patch.object(app_module.ctk, "CTkLabel", return_value=label),
        patch.object(app_module.ctk, "CTkButton", return_value=button),
        patch.object(app_module.ctk, "CTkFrame", return_value=frame),
        patch.object(app_module.ctk, "CTkEntry", return_value=entry),
        patch.object(app_module.ctk, "CTkSlider", return_value=slider),
        patch.object(app_module.ctk, "CTkOptionMenu", return_value=option_menu),
    ):
        ChronoBrightApp._build_layout(app)

    app.grid_columnconfigure.assert_called()
    label.grid.assert_called()


def test_build_morning_panel_creates_entry_and_slider() -> None:
    import chronobright.ui.app as app_module
    from chronobright.ui.app import ChronoBrightApp

    app = MagicMock(spec=[])
    app.grid = MagicMock()
    app._on_morning_slider_moved = MagicMock()
    app._translate = MagicMock(side_effect=lambda key, **_values: key)
    frame = MagicMock()
    entry = MagicMock()
    slider = MagicMock()

    with (
        patch.object(app_module.ctk, "CTkFrame", return_value=frame),
        patch.object(app_module.ctk, "CTkFont", return_value=MagicMock()),
        patch.object(app_module.ctk, "CTkLabel", return_value=MagicMock()),
        patch.object(app_module.ctk, "CTkEntry", return_value=entry),
        patch.object(app_module.ctk, "CTkSlider", return_value=slider),
    ):
        ChronoBrightApp._build_morning_panel(app)

    entry.insert.assert_called()
    slider.set.assert_called()
    slider.configure.assert_called()


def test_build_evening_panel_creates_entry_and_slider() -> None:
    import chronobright.ui.app as app_module
    from chronobright.ui.app import ChronoBrightApp

    app = MagicMock(spec=[])
    app.grid = MagicMock()
    app._on_evening_slider_moved = MagicMock()
    app._translate = MagicMock(side_effect=lambda key, **_values: key)
    frame = MagicMock()
    entry = MagicMock()
    slider = MagicMock()

    with (
        patch.object(app_module.ctk, "CTkFrame", return_value=frame),
        patch.object(app_module.ctk, "CTkFont", return_value=MagicMock()),
        patch.object(app_module.ctk, "CTkLabel", return_value=MagicMock()),
        patch.object(app_module.ctk, "CTkEntry", return_value=entry),
        patch.object(app_module.ctk, "CTkSlider", return_value=slider),
    ):
        ChronoBrightApp._build_evening_panel(app)

    entry.insert.assert_called()
    slider.set.assert_called()
    slider.configure.assert_called()
