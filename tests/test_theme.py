"""Tests for :mod:`chronobright.ui.theme`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from chronobright.ui.theme import apply_theme


@patch("chronobright.ui.theme.ctk")
def test_apply_theme_sets_appearance_and_color(mock_ctk: MagicMock) -> None:
    apply_theme()
    mock_ctk.set_appearance_mode.assert_called_once_with("System")
    mock_ctk.set_default_color_theme.assert_called_once_with("dark-blue")
