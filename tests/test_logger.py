"""Tests for :mod:`chronobright.logger`."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock

import pytest

import chronobright.logger as logger_module


@pytest.fixture(autouse=True)
def reset_logger_state() -> None:
    root = logging.getLogger("chronobright")
    root.handlers.clear()
    logger_module._configured = False
    yield
    root.handlers.clear()
    logger_module._configured = False


def test_get_logger_configures_on_first_call() -> None:
    assert logger_module._configured is False
    log = logger_module.get_logger("chronobright.test")
    assert logger_module._configured is True
    assert log.name == "chronobright.test"
    assert logging.getLogger("chronobright").handlers


def test_get_logger_is_idempotent() -> None:
    logger_module.get_logger("chronobright.test")
    handler_count = len(logging.getLogger("chronobright").handlers)
    logger_module.get_logger("chronobright.other")
    assert len(logging.getLogger("chronobright").handlers) == handler_count


def test_configure_root_logger_handles_log_dir_oserror(monkeypatch: pytest.MonkeyPatch) -> None:
    log_dir = MagicMock()
    log_dir.mkdir.side_effect = OSError("denied")
    monkeypatch.setattr(logger_module.config, "LOG_DIR", log_dir)
    monkeypatch.setattr(logger_module.config, "LOG_PATH", log_dir / "chronobright.log")

    logger_module.get_logger("chronobright.test")

    root = logging.getLogger("chronobright")
    assert any(isinstance(h, logging.StreamHandler) for h in root.handlers)
