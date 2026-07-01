"""Background scheduler that applies brightness levels at configured times."""

from __future__ import annotations

import threading
import time
from datetime import datetime, time as dt_time
from typing import Callable

import schedule

from chronobright.logger import get_logger
from chronobright.models import BrightnessScheduleConfig

logger = get_logger(__name__)


class ScheduleService:
    """Manage a daily brightness schedule running in a daemon thread."""

    def __init__(
        self,
        on_brightness_change: Callable[[int, str], None],
        poll_interval_seconds: float = 1.0,
    ) -> None:
        self._on_brightness_change = on_brightness_change
        self._poll_interval_seconds = poll_interval_seconds
        self._scheduler = schedule.Scheduler()
        self._running = threading.Event()
        self._thread: threading.Thread | None = None

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Start the background polling thread. No-op if already running."""
        if self._thread and self._thread.is_alive():
            return

        self._running.set()
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        logger.info("Schedule service started.")

    def stop(self) -> None:
        """Signal the background thread to stop at its next poll cycle."""
        self._running.clear()
        logger.info("Schedule service stopped.")

    def apply_schedule(self, config: BrightnessScheduleConfig) -> str:
        """Validate *config*, register daily jobs, and immediately apply the correct period.

        Returns a human-readable status string describing the active schedule.
        """
        config.validate()
        self._scheduler.clear()

        self._apply_immediate_brightness(config)

        self._scheduler.every().day.at(config.morning_time).do(
            self._on_brightness_change,
            config.morning_brightness,
            "Morning",
        )
        self._scheduler.every().day.at(config.evening_time).do(
            self._on_brightness_change,
            config.evening_brightness,
            "Evening",
        )

        status = (
            f"Schedule active — morning {config.morning_time} @ {config.morning_brightness}%, "
            f"evening {config.evening_time} @ {config.evening_brightness}%"
        )
        logger.info(status)
        return status

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _apply_immediate_brightness(self, config: BrightnessScheduleConfig) -> None:
        """Apply whichever period is currently active without waiting for a schedule tick."""
        now = datetime.now().time()
        morning_time = self._parse_clock(config.morning_time)
        evening_time = self._parse_clock(config.evening_time)

        if morning_time < evening_time:
            morning_active = morning_time <= now < evening_time
        else:
            morning_active = not (evening_time <= now < morning_time)

        if morning_active:
            logger.debug("Immediate apply: morning period active.")
            self._on_brightness_change(config.morning_brightness, "Morning (immediate)")
        else:
            logger.debug("Immediate apply: evening period active.")
            self._on_brightness_change(config.evening_brightness, "Evening (immediate)")

    def _run_loop(self) -> None:
        while self._running.is_set():
            self._scheduler.run_pending()
            time.sleep(self._poll_interval_seconds)

    @staticmethod
    def _parse_clock(value: str) -> dt_time:
        return datetime.strptime(value, "%H:%M").time()
