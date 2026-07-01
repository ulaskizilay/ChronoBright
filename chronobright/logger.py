"""Centralised logging configuration for ChronoBright.

All modules should obtain their logger via:

    from chronobright.logger import get_logger
    logger = get_logger(__name__)
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path


def _resolve_log_path() -> Path:
    """Return the platform-appropriate log file path."""
    import platform

    if platform.system() == "Windows":
        import os
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path.home() / ".local" / "share"

    log_dir = base / "ChronoBright" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / "chronobright.log"


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
        log_path = _resolve_log_path()
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(fmt)
        root.addHandler(file_handler)
    except OSError:
        root.warning("Could not open log file. File logging is disabled.")


_configure_root_logger()


def get_logger(name: str) -> logging.Logger:
    """Return a child logger scoped under the 'chronobright' namespace."""
    return logging.getLogger(name)
