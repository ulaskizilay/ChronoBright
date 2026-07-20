"""System tray icon management via pystray."""

from __future__ import annotations

import threading
from collections.abc import Callable

import pystray
from PIL import Image, ImageDraw

from chronobright.logger import get_logger

logger = get_logger(__name__)


class TrayService:
    """Create and manage a system tray icon with Show/Hide/Exit menu items."""

    def __init__(
        self,
        on_show_window: Callable[[], None],
        on_hide_window: Callable[[], None],
        on_exit_application: Callable[[], None],
    ) -> None:
        self._on_show_window = on_show_window
        self._on_hide_window = on_hide_window
        self._on_exit_application = on_exit_application
        self._icon: pystray.Icon | None = None
        self._thread: threading.Thread | None = None
        self._window_visible = True

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def start(self) -> None:
        """Create the tray icon and start it in a daemon thread. No-op if already running."""
        if self._thread and self._thread.is_alive():
            return

        self._icon = pystray.Icon(
            name="ChronoBright",
            title="ChronoBright",
            icon=self._create_icon_image(),
            menu=pystray.Menu(
                pystray.MenuItem("Show Window", self._show_window, default=True, enabled=self._can_show_window),
                pystray.MenuItem("Hide Window", self._hide_window, enabled=self._can_hide_window),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Exit Application", self._exit_application),
            ),
        )

        self._thread = threading.Thread(target=self._icon.run, daemon=True)
        self._thread.start()
        logger.info("Tray icon started.")

    def stop(self) -> None:
        """Stop and remove the tray icon."""
        if self._icon is None:
            return
        self._icon.stop()
        logger.info("Tray icon stopped.")

    def set_window_visible(self, is_visible: bool) -> None:
        """Update the tray menu state to reflect current window visibility."""
        self._window_visible = is_visible
        self._update_menu()

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _show_window(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._on_show_window()

    def _hide_window(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._on_hide_window()

    def _exit_application(self, icon: pystray.Icon, item: pystray.MenuItem) -> None:
        self._on_exit_application()

    def _can_show_window(self, item: pystray.MenuItem) -> bool:
        return not self._window_visible

    def _can_hide_window(self, item: pystray.MenuItem) -> bool:
        return self._window_visible

    def _update_menu(self) -> None:
        if self._icon is None:
            return
        self._icon.update_menu()

    @staticmethod
    def _create_icon_image() -> Image.Image:
        size = 64
        background_color = "#1f2937"
        accent_color = "#f59e0b"
        text_color = "#f8fafc"

        image = Image.new("RGB", (size, size), background_color)
        draw = ImageDraw.Draw(image)
        draw.rounded_rectangle((6, 6, 58, 58), radius=12, fill=background_color, outline=accent_color, width=3)
        draw.rectangle((16, 20, 48, 28), fill=accent_color)
        draw.rectangle((16, 36, 38, 44), fill=text_color)
        draw.rectangle((40, 36, 48, 44), fill=accent_color)
        return image
