"""Thin wrapper around screen-brightness-control for reading and writing display brightness."""

from __future__ import annotations

import screen_brightness_control as sbc

from chronobright.logger import get_logger

logger = get_logger(__name__)


class BrightnessService:
    """Read and set the system display brightness."""

    def get_brightness(self) -> int | None:
        """Return current brightness as an integer percentage, or None on failure."""
        try:
            result = sbc.get_brightness()
        except Exception as exc:
            logger.warning("Could not read current brightness: %s", exc)
            return None

        if isinstance(result, list):
            if not result:
                logger.warning("Brightness query returned an empty list.")
                return None
            return int(result[0])

        return int(result)

    def set_brightness(self, level: int) -> None:
        """Set display brightness to *level* percent (0–100).

        Raises:
            RuntimeError: If the underlying brightness API call fails.
        """
        try:
            sbc.set_brightness(level)
            logger.debug("Brightness set to %d%%.", level)
        except Exception as exc:
            raise RuntimeError(f"Failed to set brightness to {level}%") from exc
