"""Tests for :mod:`chronobright.__main__`."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from chronobright.__main__ import main


@patch("chronobright.__main__.ChronoBrightApp")
def test_main_starts_app(mock_app_cls: MagicMock) -> None:
    app = mock_app_cls.return_value
    main()
    app.mainloop.assert_called_once()


@patch("chronobright.__main__.ChronoBrightApp", side_effect=RuntimeError("startup failed"))
@patch("chronobright.__main__.sys.exit")
def test_main_exits_with_error_on_exception(mock_exit: MagicMock, mock_app_cls: MagicMock) -> None:
    main()
    mock_exit.assert_called_once_with(1)
