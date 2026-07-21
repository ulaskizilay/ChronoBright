"""Main application window for ChronoBright."""

from __future__ import annotations

import customtkinter as ctk

from chronobright import config
from chronobright.logger import get_logger
from chronobright.models import BrightnessScheduleConfig
from chronobright.services.brightness_service import BrightnessService
from chronobright.services.schedule_service import ScheduleService
from chronobright.services.settings_service import SettingsService
from chronobright.services.tray_service import TrayService
from chronobright.ui.theme import apply_theme

logger = get_logger(__name__)


class ChronoBrightApp(ctk.CTk):  # type: ignore[misc]
    """Top-level application window.

    Wires up the service layer and builds the UI on initialisation.
    The schedule and tray icon start immediately; the window can be hidden
    to the system tray without stopping background services.
    """

    def __init__(self) -> None:
        apply_theme()
        super().__init__()

        self.title(config.APP_TITLE)
        self.geometry(config.WINDOW_SIZE)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

        self._brightness_service = BrightnessService()
        self._startup_brightness = self._brightness_service.get_all_brightness()
        self._settings_service = SettingsService()
        self._schedule_service = ScheduleService(on_brightness_change=self._apply_brightness)
        self._tray_service = TrayService(
            on_show_window=self._show_window_from_tray,
            on_hide_window=self._hide_window_from_tray,
            on_exit_application=self._exit_from_tray,
        )
        self._is_exiting = False
        self._window_in_tray = False

        self._build_layout()
        self._load_saved_schedule()
        self._schedule_service.start()
        self._tray_service.start()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self) -> None:
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3), weight=1)

        self._header_label = ctk.CTkLabel(
            self,
            text="Display Brightness Scheduler",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self._header_label.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10))

        self._build_morning_panel()
        self._build_evening_panel()

        self._btn_apply = ctk.CTkButton(
            self, text="Save & Apply Schedule", command=self._on_apply_clicked
        )
        self._btn_apply.grid(row=2, column=0, padx=(20, 10), pady=10, sticky="ew")

        self._btn_exit = ctk.CTkButton(
            self,
            text="Exit Application",
            fg_color="#b91c1c",
            hover_color="#991b1b",
            command=self.exit_application,
        )
        self._btn_exit.grid(row=2, column=1, padx=(10, 20), pady=10, sticky="ew")

        self._lbl_status = ctk.CTkLabel(
            self, text="Status: Idle — configure and press Apply", text_color="gray"
        )
        self._lbl_status.grid(row=3, column=0, columnspan=2, padx=20, pady=10)

    def _build_morning_panel(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        self._morning_frame = frame

        ctk.CTkLabel(frame, text="Morning Settings", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=10
        )

        self._entry_morning_time = ctk.CTkEntry(
            frame, placeholder_text=config.DEFAULT_MORNING_TIME
        )
        self._entry_morning_time.insert(0, config.DEFAULT_MORNING_TIME)
        self._entry_morning_time.grid(row=1, column=0, padx=20, pady=5)

        self._slider_morning = ctk.CTkSlider(frame, from_=0, to=100, number_of_steps=100)
        self._slider_morning.set(config.DEFAULT_MORNING_BRIGHTNESS)
        self._slider_morning.grid(row=2, column=0, padx=20, pady=5)
        self._slider_morning.configure(command=self._on_morning_slider_moved)

        self._lbl_morning_value = ctk.CTkLabel(
            frame, text=f"Brightness: {config.DEFAULT_MORNING_BRIGHTNESS}%"
        )
        self._lbl_morning_value.grid(row=3, column=0, pady=(0, 10))

    def _build_evening_panel(self) -> None:
        frame = ctk.CTkFrame(self)
        frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        frame.grid_columnconfigure(0, weight=1)
        self._evening_frame = frame

        ctk.CTkLabel(frame, text="Evening Settings", font=ctk.CTkFont(weight="bold")).grid(
            row=0, column=0, padx=10, pady=10
        )

        self._entry_evening_time = ctk.CTkEntry(
            frame, placeholder_text=config.DEFAULT_EVENING_TIME
        )
        self._entry_evening_time.insert(0, config.DEFAULT_EVENING_TIME)
        self._entry_evening_time.grid(row=1, column=0, padx=20, pady=5)

        self._slider_evening = ctk.CTkSlider(frame, from_=0, to=100, number_of_steps=100)
        self._slider_evening.set(config.DEFAULT_EVENING_BRIGHTNESS)
        self._slider_evening.grid(row=2, column=0, padx=20, pady=5)
        self._slider_evening.configure(command=self._on_evening_slider_moved)

        self._lbl_evening_value = ctk.CTkLabel(
            frame, text=f"Brightness: {config.DEFAULT_EVENING_BRIGHTNESS}%"
        )
        self._lbl_evening_value.grid(row=3, column=0, pady=(0, 10))

    # ------------------------------------------------------------------
    # Event handlers
    # ------------------------------------------------------------------

    def _on_morning_slider_moved(self, value: float) -> None:
        self._lbl_morning_value.configure(text=f"Brightness: {int(value)}%")

    def _on_evening_slider_moved(self, value: float) -> None:
        self._lbl_evening_value.configure(text=f"Brightness: {int(value)}%")

    def _on_apply_clicked(self) -> None:
        # Save first, then apply atomically. If save_schedule raises OSError on disk
        # failure, apply_schedule is never called and the in-memory scheduler is left
        # untouched (yesterday's schedule keeps running). ValueError here can only come
        # from _read_form_config validating an empty/invalid entry.
        try:
            schedule_config = self._read_form_config()
            self._settings_service.save_schedule(schedule_config)
            status = self._schedule_service.apply_schedule(schedule_config)
            self._set_status(f"{status} [saved]", "green")
        except ValueError as exc:
            logger.warning("Invalid schedule input: %s", exc)
            self._set_status(f"Invalid input: {exc}", "red")
        except OSError as exc:
            logger.error("Failed to save config: %s", exc)
            self._set_status(f"Could not save config: {exc}", "red")

    def _on_window_close(self) -> None:
        self.hide_window_to_tray()

    # ------------------------------------------------------------------
    # Public interface called by the schedule or tray service
    # ------------------------------------------------------------------

    def _apply_brightness(self, level: int, period_name: str) -> None:
        """Set the display brightness and update the status bar (thread-safe)."""
        target = int(level)
        logger.info("Applying %s brightness: %d%%", period_name, target)

        try:
            self._brightness_service.set_brightness(target)
            self._update_status_safe(f"Set to {target}% ({period_name})", "blue")
        except RuntimeError as exc:
            logger.error("%s", exc)
            self._update_status_safe("Error — check logs for details", "red")

    def hide_window_to_tray(self) -> None:
        """Withdraw the window without stopping background services."""
        if self._is_exiting or self._window_in_tray:
            return

        self.withdraw()
        self._window_in_tray = True
        self._tray_service.set_window_visible(False)
        logger.info("Window hidden to tray.")

    def show_window(self) -> None:
        """Restore the window from the system tray."""
        if self._is_exiting:
            return

        self.deiconify()
        self.lift()
        self.focus_force()
        self._window_in_tray = False
        self._tray_service.set_window_visible(True)
        logger.info("Window restored from tray.")

    def exit_application(self) -> None:
        """Shut down all services, restore startup brightness, and destroy the window."""
        if self._is_exiting:
            return

        self._is_exiting = True
        logger.info("Shutting down application.")
        self._tray_service.stop()
        self._schedule_service.stop()
        self._restore_startup_brightness()
        self.destroy()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _show_window_from_tray(self) -> None:
        self.after(0, self.show_window)

    def _hide_window_from_tray(self) -> None:
        self.after(0, self.hide_window_to_tray)

    def _exit_from_tray(self) -> None:
        self.after(0, self.exit_application)

    def _load_saved_schedule(self) -> None:
        result = self._settings_service.load_schedule()
        self._populate_form(result.config)

        if result.source == "saved":
            status = self._schedule_service.apply_schedule(result.config)
            self._set_status(f"{status} [loaded]", "green")
            return

        if result.source == "fallback":
            self._set_status("Corrupt config detected — defaults loaded", "red")
            return

        self._set_status("No saved config — configure and press Apply", "gray")

    def _populate_form(self, schedule_config: BrightnessScheduleConfig) -> None:
        self._entry_morning_time.delete(0, "end")
        self._entry_morning_time.insert(0, schedule_config.morning_time)
        self._slider_morning.set(schedule_config.morning_brightness)
        self._on_morning_slider_moved(schedule_config.morning_brightness)

        self._entry_evening_time.delete(0, "end")
        self._entry_evening_time.insert(0, schedule_config.evening_time)
        self._slider_evening.set(schedule_config.evening_brightness)
        self._on_evening_slider_moved(schedule_config.evening_brightness)

    def _read_form_config(self) -> BrightnessScheduleConfig:
        cfg = BrightnessScheduleConfig(
            morning_time=self._entry_morning_time.get(),
            morning_brightness=int(self._slider_morning.get()),
            evening_time=self._entry_evening_time.get(),
            evening_brightness=int(self._slider_evening.get()),
        )
        cfg.validate()
        return cfg

    def _update_status_safe(self, text: str, color: str) -> None:
        self.after(0, lambda: self._set_status(text, color))

    def _set_status(self, text: str, color: str) -> None:
        self._lbl_status.configure(text=f"Status: {text}", text_color=color)

    def _restore_startup_brightness(self) -> None:
        if self._startup_brightness is None:
            logger.warning("Skipping brightness restore — initial brightness could not be read.")
            return

        try:
            if len(self._startup_brightness) == 1:
                self._brightness_service.set_brightness(self._startup_brightness[0])
            else:
                for index, level in enumerate(self._startup_brightness):
                    self._brightness_service.set_brightness(level, display=index)
            logger.info(
                "Restored startup brightness for %d display(s).",
                len(self._startup_brightness),
            )
        except RuntimeError as exc:
            logger.error("Failed to restore startup brightness: %s", exc)
