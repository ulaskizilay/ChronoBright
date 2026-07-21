"""Background scheduler that applies brightness levels at configured times."""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from datetime import datetime

from chronobright.logger import get_logger
from chronobright.models import BrightnessScheduleConfig
from chronobright.time_utils import is_morning_period_active

logger = get_logger(__name__)

PeriodName = str  # "morning" | "evening"


class ScheduleService:
    """Manage a daily brightness schedule running in a daemon thread.

    Period transitions are detected by polling the active schedule window instead
    of firing one-shot wall-clock jobs. This avoids duplicate or skipped triggers
    during daylight-saving time changes.
    """

    def __init__(
        self,
        on_brightness_change: Callable[[int, str], None],
        poll_interval_seconds: float = 1.0,
    ) -> None:
        self._on_brightness_change = on_brightness_change
        self._poll_interval_seconds = poll_interval_seconds
        self._running = threading.Event()
        self._thread: threading.Thread | None = None
        self._config: BrightnessScheduleConfig | None = None
        self._active_period: PeriodName | None = None

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
        """Signal the background thread to stop and wait for it to finish."""
        self._running.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2.0)
        logger.info("Schedule service stopped.")

    @property
    def job_count(self) -> int:
        """Number of configured schedule transitions (morning + evening)."""
        return 2 if self._config is not None else 0

    @property
    def active_period(self) -> PeriodName | None:
        """Currently active schedule period, if a schedule is loaded."""
        return self._active_period

    def replace_brightness_callback(self, callback: Callable[[int, str], None]) -> None:
        """Swap the brightness-change callback."""
        self._on_brightness_change = callback

    def apply_schedule(self, config: BrightnessScheduleConfig) -> str:
        """Validate *config*, store it, and immediately apply the correct period.

        Returns a human-readable status string describing the active schedule.
        """
        config.validate()
        self._config = config
        self._apply_immediate_brightness(config)

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
        """Apply whichever period is currently active without waiting for a poll tick."""
        period = self._current_period(config)
        self._active_period = period
        level, label = self._period_settings(config, period)
        logger.debug("Immediate apply: %s period active.", period)
        self._on_brightness_change(level, f"{label} (immediate)")

    def _run_loop(self) -> None:
        while self._running.is_set():
            try:
                self._check_period_transition()
            except Exception:
                logger.exception("Schedule loop error")
                self._running.clear()
            time.sleep(self._poll_interval_seconds)

    def _check_period_transition(self) -> None:
        if self._config is None:
            return

        period = self._current_period(self._config)
        if period == self._active_period:
            return

        self._active_period = period
        level, label = self._period_settings(self._config, period)
        logger.info("Schedule period changed to %s.", period)
        self._on_brightness_change(level, label)

    @staticmethod
    def _current_period(config: BrightnessScheduleConfig) -> PeriodName:
        now = datetime.now().time()
        if is_morning_period_active(config.morning_time, config.evening_time, now):
            return "morning"
        return "evening"

    @staticmethod
    def _period_settings(config: BrightnessScheduleConfig, period: PeriodName) -> tuple[int, str]:
        if period == "morning":
            return config.morning_brightness, "Morning"
        return config.evening_brightness, "Evening"
