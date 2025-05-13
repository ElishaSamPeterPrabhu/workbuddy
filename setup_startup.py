"""
Windows startup integration script for WorkBuddy (Jarvis Assistant).

Adds or removes the application from Windows startup.

TODO: Update the entry point if the main script moves during modularization.
"""

import os
import sys
import winreg
import pythoncom
import win32com.client
from pathlib import Path


def setup_startup_shortcut():
    """Create a shortcut in the Windows Startup folder to launch the application on system startup"""
    try:
        # Get path to the main script
        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "main.py")
        )
        python_exe = sys.executable

        # Create the command to run
        cmd = f'"{python_exe}" "{script_path}"'

        # Get the Startup folder path
        startup_folder = os.path.join(
            os.environ["APPDATA"],
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup",
        )
        shortcut_path = os.path.join(startup_folder, "WorkBuddy.lnk")

        # Create the shortcut
        pythoncom.CoInitialize()  # Initialize COM
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(shortcut_path)
        shortcut.Targetpath = python_exe
        shortcut.Arguments = f'"{script_path}"'
        shortcut.WorkingDirectory = os.path.dirname(script_path)
        shortcut.Description = "WorkBuddy AI Assistant"
        shortcut.IconLocation = os.path.join(os.path.dirname(script_path), "icon.png")
        shortcut.save()

        print(f"Startup shortcut created at: {shortcut_path}")
        return True
    except Exception as e:
        print(f"Error creating startup shortcut: {str(e)}")
        return False


def setup_registry_startup():
    """Add the application to the Windows registry to run at startup"""
    try:
        # Get path to the main script
        script_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "main.py")
        )
        python_exe = sys.executable

        # Create the command to run
        cmd = f'"{python_exe}" "{script_path}"'

        # Open the registry key
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )

        # Set the value
        winreg.SetValueEx(key, "WorkBuddy", 0, winreg.REG_SZ, cmd)
        winreg.CloseKey(key)

        print("Registry startup entry created")
        return True
    except Exception as e:
        print(f"Error creating registry startup entry: {str(e)}")
        return False


def remove_from_startup():
    """Remove the application from Windows startup"""
    try:
        # Remove shortcut if it exists
        startup_folder = os.path.join(
            os.environ["APPDATA"],
            "Microsoft",
            "Windows",
            "Start Menu",
            "Programs",
            "Startup",
        )
        shortcut_path = os.path.join(startup_folder, "WorkBuddy.lnk")

        if os.path.exists(shortcut_path):
            os.remove(shortcut_path)
            print(f"Removed startup shortcut: {shortcut_path}")

        # Remove registry entry
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_SET_VALUE,
        )

        try:
            winreg.DeleteValue(key, "WorkBuddy")
            print("Removed registry startup entry")
        except FileNotFoundError:
            pass  # Registry key didn't exist

        winreg.CloseKey(key)

        return True
    except Exception as e:
        print(f"Error removing from startup: {str(e)}")
        return False


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Configure WorkBuddy startup settings")
    parser.add_argument("--enable", action="store_true", help="Enable startup at boot")
    parser.add_argument(
        "--disable", action="store_true", help="Disable startup at boot"
    )

    args = parser.parse_args()

    if args.enable:
        print("Setting up WorkBuddy to run at startup...")
        success1 = setup_startup_shortcut()
        success2 = setup_registry_startup()

        if success1 or success2:
            print("WorkBuddy will now run when you log into Windows.")
        else:
            print("Failed to set up auto-start. Please try running as administrator.")

    elif args.disable:
        print("Removing WorkBuddy from startup...")
        success = remove_from_startup()

        if success:
            print("WorkBuddy will no longer run at startup.")
        else:
            print("Failed to remove from startup. Please try running as administrator.")

    else:
        print("Please specify --enable or --disable")
