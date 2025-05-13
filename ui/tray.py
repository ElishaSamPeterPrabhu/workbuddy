"""
PyQt6 System Tray Integration for WorkBuddy (Jarvis Assistant).

This module provides the system tray icon and menu for the assistant, with actions to show/hide the overlay, open settings, and quit.
"""

from typing import Optional
from PyQt6.QtWidgets import QSystemTrayIcon, QMenu, QWidget
from PyQt6.QtGui import QIcon, QAction
from .overlay import OverlayWindow
import os


class WorkBuddyTray(QSystemTrayIcon):
    """
    System tray icon and menu for WorkBuddy.
    """

    def __init__(
        self, overlay: OverlayWindow, parent: Optional[QWidget] = None
    ) -> None:
        """
        Initialize the system tray icon and menu.

        Args:
            overlay: The overlay chat window to control.
            parent: Optional parent widget.
        """
        # Try to use assets/workbuddy_icon.png, fallback to icon.png at root, else use default
        icon_path = "assets/workbuddy_icon.png"
        if not os.path.exists(icon_path):
            icon_path = "icon.png"
        if os.path.exists(icon_path):
            icon = QIcon(icon_path)
        else:
            icon = QIcon()  # Empty icon, will show warning
        super().__init__(icon, parent)
        self.overlay = overlay
        self.menu = QMenu(parent)
        self._init_menu()
        self.setContextMenu(self.menu)

    def _init_menu(self) -> None:
        """
        Set up the tray menu actions.
        """
        show_action = QAction("Show/Hide", self)
        show_action.triggered.connect(self.on_show_hide)
        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(self.on_settings)
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.on_quit)
        self.menu.addAction(show_action)
        self.menu.addAction(settings_action)
        self.menu.addSeparator()
        self.menu.addAction(quit_action)

    def on_show_hide(self) -> None:
        """
        Handle the Show/Hide action by toggling the overlay window.
        """
        if self.overlay.isVisible():
            self.overlay.hide_overlay()
        else:
            self.overlay.show_overlay()

    def on_settings(self) -> None:
        """
        Handle the Settings action.
        """
        # TODO: Open settings dialog
        pass

    def on_quit(self) -> None:
        """
        Handle the Quit action.
        """
        # TODO: Clean up and quit application
        self.overlay.hide_overlay()
        self.parent().close() if self.parent() else None
        # Optionally, call QApplication.quit() if needed
