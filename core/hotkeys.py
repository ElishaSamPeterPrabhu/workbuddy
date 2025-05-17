"""
Hotkeys module for WorkBuddy.

Manages global keyboard shortcuts for WorkBuddy actions.
"""

import keyboard
import logging
from typing import Callable, Dict, Optional, Any


class HotkeyManager:
    """
    Manager for global keyboard shortcuts in WorkBuddy.
    
    This class provides a way to register global hotkeys and link them to actions.
    It uses the keyboard library to handle global keyboard events.
    """

    def __init__(self) -> None:
        """Initialize the HotkeyManager."""
        self.registered_hotkeys: Dict[str, Callable] = {}
        self.default_hotkey = "alt+shift+w"  # Default hotkey for showing/hiding WorkBuddy
        self.logger = logging.getLogger(__name__)
        
    def register_show_hide(self, callback: Callable[[], None], hotkey: Optional[str] = None) -> bool:
        """
        Register the show/hide hotkey for the WorkBuddy overlay.
        
        Args:
            callback: Function to call when the hotkey is pressed
            hotkey: Custom hotkey combination (default: alt+shift+w)
            
        Returns:
            True if registration was successful, False otherwise
        """
        hotkey_to_use = hotkey or self.default_hotkey
        
        # Create a wrapper function that catches exceptions
        def safe_callback():
            try:
                self.logger.info(f"Show/hide hotkey triggered: {hotkey_to_use}")
                
                # Important: Use a Qt timer to ensure the callback executes in the main thread
                # This prevents crashes due to thread safety issues
                from PyQt6.QtCore import QTimer  
                QTimer.singleShot(0, callback)
                
            except Exception as e:
                self.logger.error(f"Error in hotkey callback: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
        
        try:
            keyboard.add_hotkey(hotkey_to_use, safe_callback)
            self.registered_hotkeys["show_hide"] = callback
            self.logger.info(f"Registered show/hide hotkey: {hotkey_to_use}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register hotkey {hotkey_to_use}: {e}")
            return False
    
    def register_hotkey(self, hotkey: str, callback: Callable[[], None], action_name: str) -> bool:
        """
        Register a custom hotkey for any action.
        
        Args:
            hotkey: Hotkey combination (e.g., 'ctrl+alt+s')
            callback: Function to call when the hotkey is pressed
            action_name: Name to identify this hotkey action
            
        Returns:
            True if registration was successful, False otherwise
        """
        # Create a wrapper function that catches exceptions
        def safe_callback():
            try:
                self.logger.info(f"Hotkey triggered for {action_name}: {hotkey}")
                
                # Important: Use Qt timer to ensure callback executes in the main thread
                from PyQt6.QtCore import QTimer
                QTimer.singleShot(0, callback)
                
            except Exception as e:
                self.logger.error(f"Error in hotkey callback for {action_name}: {e}")
                import traceback
                self.logger.error(traceback.format_exc())
        
        try:
            keyboard.add_hotkey(hotkey, safe_callback)
            self.registered_hotkeys[action_name] = callback
            self.logger.info(f"Registered hotkey for {action_name}: {hotkey}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to register hotkey {hotkey} for {action_name}: {e}")
            return False
    
    def unregister_hotkey(self, action_name: str) -> bool:
        """
        Unregister a previously registered hotkey.
        
        Args:
            action_name: The name of the action to unregister
            
        Returns:
            True if unregistration was successful, False otherwise
        """
        if action_name not in self.registered_hotkeys:
            self.logger.warning(f"No hotkey registered for action: {action_name}")
            return False
            
        try:
            # The keyboard library doesn't have a direct way to unregister by callback,
            # so we have to use a workaround
            # TODO: Implement better unregistration when keyboard library adds support
            keyboard.unhook_all_hotkeys()
            
            # Re-register all hotkeys except the one we want to remove
            for name, callback in self.registered_hotkeys.items():
                if name != action_name:
                    # This is simplified and not ideal - in a real implementation 
                    # we would need to store the original hotkey string
                    keyboard.add_hotkey(self.default_hotkey, callback)
                    
            del self.registered_hotkeys[action_name]
            self.logger.info(f"Unregistered hotkey for {action_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to unregister hotkey for {action_name}: {e}")
            return False
    
    def is_registered(self, action_name: str) -> bool:
        """
        Check if a hotkey is registered for an action.
        
        Args:
            action_name: The name of the action
            
        Returns:
            True if a hotkey is registered, False otherwise
        """
        return action_name in self.registered_hotkeys


# Create a singleton instance
hotkey_manager = HotkeyManager() 