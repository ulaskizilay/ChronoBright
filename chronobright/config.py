"""Application-wide constants and default configuration values."""

from __future__ import annotations

import platform
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


def _resolve_config_dir() -> Path:
    """Return the platform-appropriate directory for user configuration."""
    system = platform.system()

    if system == "Windows":
        import os
        appdata = os.environ.get("APPDATA")
        base = Path(appdata) if appdata else Path.home() / "AppData" / "Roaming"
        return base / APP_NAME

    # macOS and Linux
    xdg_config = Path.home() / ".config"
    return xdg_config / APP_NAME.lower()


CONFIG_DIR: Path = _resolve_config_dir()
USER_CONFIG_PATH: Path = CONFIG_DIR / "config.json"
