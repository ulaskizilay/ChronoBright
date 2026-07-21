"""Application-wide constants, platform-aware paths, and shared validators."""

from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "ChronoBright"
APP_TITLE = "ChronoBright"
WINDOW_SIZE = "520x400"

APPEARANCE_MODE = "System"
COLOR_THEME = "dark-blue"

DEFAULT_MORNING_TIME = "08:00"
DEFAULT_EVENING_TIME = "19:00"
DEFAULT_MORNING_BRIGHTNESS = 90
DEFAULT_EVENING_BRIGHTNESS = 80


def _resolve_base_dir() -> Path:
    """Return the Windows AppData Roaming directory for user data."""
    appdata = os.environ.get("APPDATA")
    return Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"


CONFIG_DIR: Path = _resolve_base_dir() / APP_NAME
LOG_DIR: Path = CONFIG_DIR / "logs"
USER_CONFIG_PATH: Path = CONFIG_DIR / "config.json"
LOG_PATH: Path = LOG_DIR / "chronobright.log"


def validate_brightness_level(level: object) -> None:
    """Reject levels that aren't plain integers in the 0–100 percent range.

    Booleans are explicitly rejected even though `bool` subclasses `int`, because
    ``True``/``False`` in a brightness field almost always indicates a bug in the
    caller (e.g. a missing type check on deserialised JSON).
    """
    if isinstance(level, bool) or not isinstance(level, int) or not 0 <= level <= 100:
        raise ValueError(f"Brightness must be an integer between 0 and 100: {level}")
