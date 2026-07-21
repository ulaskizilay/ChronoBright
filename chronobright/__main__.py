"""Allow running the package directly with `python -m chronobright`."""

from __future__ import annotations

import sys

from chronobright.logger import get_logger
from chronobright.ui.app import ChronoBrightApp

logger = get_logger(__name__)


def main() -> None:
    try:
        app = ChronoBrightApp()
        app.mainloop()
    except Exception:
        logger.exception("Fatal error in application")
        sys.exit(1)


if __name__ == "__main__":
    main()
