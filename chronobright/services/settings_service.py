"""Persist and restore user schedule configuration to disk."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

from chronobright import config
from chronobright.config import validate_brightness_level
from chronobright.logger import get_logger
from chronobright.models import BrightnessScheduleConfig

logger = get_logger(__name__)


@dataclass(frozen=True)
class SettingsLoadResult:
    """Outcome of a settings load operation."""

    config: BrightnessScheduleConfig
    source: str  # "saved" | "fallback" | "missing"


class SettingsService:
    """Read and write schedule configuration to a JSON file on disk."""

    def __init__(self, config_path: Path = config.USER_CONFIG_PATH) -> None:
        self._config_path = config_path

    def load_schedule(self) -> SettingsLoadResult:
        """Load the schedule from disk.

        Returns a :class:`SettingsLoadResult` whose *source* field indicates
        whether the data came from a saved file, defaults due to a missing file,
        or defaults due to a corrupt/invalid file.
        """
        if not self._config_path.exists():
            logger.info("No config file found at %s — using defaults.", self._config_path)
            return SettingsLoadResult(config=self._default_config(), source="missing")

        try:
            with self._config_path.open("r", encoding="utf-8") as fh:
                payload = json.load(fh)

            schedule_config = BrightnessScheduleConfig(
                morning_time=str(payload["morning_time"]),
                morning_brightness=self._parse_brightness(payload["morning_brightness"]),
                evening_time=str(payload["evening_time"]),
                evening_brightness=self._parse_brightness(payload["evening_brightness"]),
            )
            logger.info("Loaded schedule from %s.", self._config_path)
            return SettingsLoadResult(config=schedule_config, source="saved")

        except (OSError, TypeError, ValueError, KeyError, json.JSONDecodeError) as exc:
            logger.warning(
                "Failed to load config from %s: %s. Falling back to defaults.",
                self._config_path,
                exc,
            )
            return SettingsLoadResult(config=self._default_config(), source="fallback")

    def save_schedule(self, schedule_config: BrightnessScheduleConfig) -> None:
        """Validate and persist *schedule_config* to disk atomically.

        Raises:
            ValueError: If *schedule_config* contains invalid values.
            OSError: If the config file cannot be written.
        """
        schedule_config.validate()

        payload = {
            "morning_time": schedule_config.morning_time,
            "morning_brightness": schedule_config.morning_brightness,
            "evening_time": schedule_config.evening_time,
            "evening_brightness": schedule_config.evening_brightness,
        }

        self._config_path.parent.mkdir(parents=True, exist_ok=True)

        tmp_path = self._config_path.with_suffix(".json.tmp")
        with tmp_path.open("w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        os.replace(tmp_path, self._config_path)

        logger.info("Schedule saved to %s.", self._config_path)

    @staticmethod
    def _parse_brightness(value: object) -> int:
        """Parse a JSON brightness value, rejecting bools before ``int()`` coercion."""
        validate_brightness_level(value)
        if not isinstance(value, int):
            raise ValueError(f"Brightness must be an integer between 0 and 100: {value}")
        return value

    @staticmethod
    def _default_config() -> BrightnessScheduleConfig:
        return BrightnessScheduleConfig(
            morning_time=config.DEFAULT_MORNING_TIME,
            morning_brightness=config.DEFAULT_MORNING_BRIGHTNESS,
            evening_time=config.DEFAULT_EVENING_TIME,
            evening_brightness=config.DEFAULT_EVENING_BRIGHTNESS,
        )
