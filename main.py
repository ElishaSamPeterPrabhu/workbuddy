"""
Main entry point for WorkBuddy (Jarvis Assistant).

Launches the PyQt6 overlay chat window and system tray integration.
Now includes enhanced Gmail and Calendar intelligence features.
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

# Enhanced features
try:
    from core.enhanced_morning_briefing import EnhancedMorningBriefing
    ENHANCED_FEATURES_AVAILABLE = True
    logging.info("Enhanced Gmail and Calendar features loaded successfully")
except ImportError as e:
    logging.warning(f"Enhanced features not available: {e}")
    ENHANCED_FEATURES_AVAILABLE = False


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
    Now includes enhanced morning briefing on startup.
    """
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    overlay = OverlayWindow()
    tray = WorkBuddyTray(overlay)
    tray.show()

    # Register the global hotkey for showing/hiding the overlay
    hotkey_manager.register_show_hide(overlay.toggle_visibility)
    logging.info("Global hotkey registered: Alt+Shift+W to show/hide WorkBuddy")

    # Enhanced morning briefing on startup
    if ENHANCED_FEATURES_AVAILABLE:
        try:
            enhanced_briefing = EnhancedMorningBriefing()
            if enhanced_briefing.should_deliver_enhanced_briefing():
                logging.info("Delivering enhanced morning briefing...")
                briefing_data = enhanced_briefing.deliver_enhanced_briefing()
                logging.info(f"Enhanced briefing delivered: {briefing_data.get('type', 'unknown')} type")
            else:
                logging.info("Enhanced morning briefing not needed at this time")
        except Exception as e:
            logging.error(f"Enhanced morning briefing failed: {e}")
            # Fallback to basic briefing if needed
            try:
                from core.morning_briefing import MorningBriefing
                basic_briefing = MorningBriefing()
                if basic_briefing.should_deliver_briefing():
                    basic_briefing.deliver_briefing()
                    logging.info("Delivered basic morning briefing as fallback")
            except Exception as fallback_error:
                logging.error(f"Even basic briefing failed: {fallback_error}")

    sys.exit(app.exec())


if __name__ == "__main__":
    setup_logging()
    main()
