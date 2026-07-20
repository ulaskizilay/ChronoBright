"""Smoke test for :mod:`chronobright.ui.app`.

A full GUI smoke test requires a display backend and is out of scope for headless
CI. Importing the module at least guards against regressions in the import graph
(e.g. circular imports introduced by changes to ``__init__.py`` re-exports).
"""

from __future__ import annotations


def test_app_module_imports_cleanly() -> None:
    """Importing :mod:`chronobright.ui.app` must not raise (circular-import guard)."""

    import chronobright.ui.app  # noqa: F401
