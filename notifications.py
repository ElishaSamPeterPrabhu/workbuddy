"""
Notification module for WorkBuddy (Jarvis Assistant).

Handles Windows toast notifications with custom app name and icon using winotify.
"""

from winotify import Notification, audio
import os
from typing import Optional


def show_notification(title: str, message: str, icon_path: Optional[str] = None) -> int:
    """
    Show a Windows toast notification with custom app name and icon.

    Args:
        title: The notification title.
        message: The notification message.
        icon_path: Optional path to the icon file (PNG).

    Returns:
        0 if successful, 1 if an error occurred.
    """
    try:
        if icon_path is None:
            # Default to assets/workbuddy_icon.png
            icon_path = os.path.abspath(os.path.join("assets", "workbuddy_icon.png"))
        toast = Notification(
            app_id="WorkBuddy",  # This sets the app name!
            title=title,
            msg=message,
            icon=icon_path if os.path.exists(icon_path) else None,
        )
        toast.set_audio(audio.Default, loop=False)
        toast.show()
        return 0
    except Exception as e:
        print(f"Notification error: {e}")
        return 1
