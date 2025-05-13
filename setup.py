"""
Setup and packaging script for WorkBuddy (Jarvis Assistant).

Handles building the Windows executable and packaging all assets and modules.

TODO: Ensure all assets and modular directories are included in the build.
"""

import os
import sys
import subprocess
import platform
import importlib.util
import time


def check_python_version():
    """Check if Python version is compatible (3.8+)"""
    major, minor = sys.version_info[:2]
    if major < 3 or (major == 3 and minor < 8):
        print(f"Error: Python 3.8+ is required. You have Python {major}.{minor}")
        return False
    return True


def install_dependencies():
    """Install required packages using pip"""
    print("Installing dependencies...")

    # Get requirements.txt path
    requirements_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "requirements.txt"
    )

    # Check if requirements.txt exists
    if not os.path.exists(requirements_path):
        print("Error: requirements.txt not found.")
        return False

    try:
        # Install dependencies
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", requirements_path]
        )
        print("Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error installing dependencies: {e}")
        return False


def check_dependencies():
    """Check if all required packages are installed"""
    print("Checking dependencies...")

    required_packages = [
        "PyQt6",
        "requests",
        "SpeechRecognition",
        "pyttsx3",
        "psutil",
        "pywin32",
        "pillow",
    ]

    missing_packages = []

    for package in required_packages:
        if importlib.util.find_spec(package.lower()) is None:
            missing_packages.append(package)

    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
        return False

    print("All dependencies are installed.")
    return True


def setup_api_key():
    """Prompt user for API key and set up environment variable"""
    print("\nSetting up API key (optional but recommended)")
    print("Note: You can skip this step by pressing Enter")
    print("You can use the Trimble Cloud AI API for enhanced capabilities")

    api_key = input(
        "Enter your Trimble API token (leave empty to use default): "
    ).strip()

    if not api_key:
        print("Using default API token. The assistant will use the built-in token.")
        return

    # Set temporary environment variable
    os.environ["TRIMBLE_API_TOKEN"] = api_key

    # Provide instructions for permanent setup
    if platform.system() == "Windows":
        print("\nTo permanently set the API key, run these commands in PowerShell:")
        print(
            f'[Environment]::SetEnvironmentVariable("TRIMBLE_API_TOKEN", "{api_key}", "User")'
        )
    else:
        print(
            "\nTo permanently set the API key, add this line to your .bashrc or .zshrc:"
        )
        print(f'export TRIMBLE_API_TOKEN="{api_key}"')

    print("\nAPI token set for the current session.")


def create_app_icon():
    """Create application icon if it doesn't exist"""
    print("\nCreating application icon...")
    try:
        icon_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "create_icon.py"
        )
        subprocess.check_call([sys.executable, icon_script])
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error creating icon: {e}")
        return False


def configure_startup():
    """Ask user if they want to configure startup"""
    print("\nDo you want WorkBuddy to start automatically when you log in?")
    choice = input("Configure startup? (y/n): ").strip().lower()

    if choice == "y":
        try:
            startup_script = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "setup_startup.py"
            )
            subprocess.check_call([sys.executable, startup_script, "--enable"])
            return True
        except subprocess.CalledProcessError as e:
            print(f"Error configuring startup: {e}")
            return False
    else:
        print("Skipping startup configuration.")
        return True


def run_application():
    """Run the application for the first time"""
    print("\nDo you want to run WorkBuddy now?")
    choice = input("Run WorkBuddy? (y/n): ").strip().lower()

    if choice == "y":
        print("\nStarting WorkBuddy...")
        try:
            main_script = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "main.py"
            )
            subprocess.Popen([sys.executable, main_script])
            print("WorkBuddy is running!")
            return True
        except Exception as e:
            print(f"Error running application: {e}")
            return False
    else:
        print("\nYou can run WorkBuddy later with: python main.py")
        return True


def main():
    """Main setup function"""
    print("=" * 70)
    print("WorkBuddy Setup".center(70))
    print("=" * 70)

    # Check Python version
    if not check_python_version():
        print("Setup aborted due to incompatible Python version.")
        sys.exit(1)

    # Check if dependencies are installed, install if needed
    if not check_dependencies():
        print("Some dependencies are missing. Installing now...")
        if not install_dependencies():
            print("Failed to install dependencies. Please install them manually:")
            print("pip install -r requirements.txt")
            sys.exit(1)

    # Create icon
    create_app_icon()

    # Set up API key
    setup_api_key()

    # Configure startup
    configure_startup()

    # Run application
    run_application()

    print("\n" + "=" * 70)
    print("Setup Complete!".center(70))
    print("=" * 70)
    print("\nThank you for installing WorkBuddy AI Assistant!")
    print("For help and more information, see the README.md file.")


if __name__ == "__main__":
    main()
