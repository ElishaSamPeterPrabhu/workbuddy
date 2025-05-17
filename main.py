"""
Main entry point for WorkBuddy (Jarvis Assistant).

Launches the PyQt6 overlay chat window and system tray integration.
"""

import sys
from PyQt6.QtWidgets import QApplication
from ui.overlay import OverlayWindow
from ui.tray import WorkBuddyTray
from core.hotkeys import hotkey_manager
import logging
import os
import getpass
from dotenv import load_dotenv

load_dotenv()


def setup_logging() -> None:
    """Configure file-based logging for the application."""
    from core.storage import DB_DIR

    log_path = os.path.join(DB_DIR, "workbuddy.log")
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_path, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )
    logging.info(f"WorkBuddy started by user={getpass.getuser()}")


def main() -> None:
    """
    Start the WorkBuddy assistant application with overlay and tray.
    """
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    overlay = OverlayWindow()
    tray = WorkBuddyTray(overlay)
    tray.show()

    # Register the global hotkey for showing/hiding the overlay
    hotkey_manager.register_show_hide(overlay.toggle_visibility)
    logging.info("Global hotkey registered: Alt+Shift+W to show/hide WorkBuddy")

    sys.exit(app.exec())


if __name__ == "__main__":
    setup_logging()
    main()
