"""Centralised logging configuration for ChronoBright.

All modules should obtain their logger via:

    from chronobright.logger import get_logger
    logger = get_logger(__name__)
"""

from __future__ import annotations

import logging
import logging.handlers
import sys

from chronobright import config


def _configure_root_logger() -> None:
    """Set up the root logger once at import time."""
    root = logging.getLogger("chronobright")
    if root.handlers:
        return  # already configured

    root.setLevel(logging.DEBUG)

    fmt = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Console handler — INFO and above
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(fmt)
    root.addHandler(console_handler)

    # File handler — DEBUG and above (rotated manually; keep simple for v1)
    try:
        config.LOG_DIR.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            config.LOG_PATH,
            maxBytes=2 * 1024 * 1024,
            backupCount=3,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    except OSError:
        root.warning("Could not open log file. File logging is disabled.")


_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a child logger scoped under the 'chronobright' namespace."""
    return logging.getLogger(name)
