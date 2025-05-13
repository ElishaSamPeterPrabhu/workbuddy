# WorkBuddy (Jarvis Assistant)

A modern, AI-powered desktop assistant for software engineers, built with Python and PyQt6. WorkBuddy sits in your system tray, provides a translucent chat overlay, and integrates with GitHub and Google Calendar to boost your productivity.

## Features

1. **Auto-Start & System Tray Presence**
2. **Translucent Chat Overlay (PyQt6)**
3. **GitHub Integration** (assigned issues, PRs, reviews)
4. **Google Calendar Integration** (agenda, reminders)
5. **Smart Notifications Center**
6. **Persistent Memory & Reminders**
7. **Daily Briefing**
8. **Quick Command Bar**
9. **Contextual Suggestions**
10. **Customizable Settings & Privacy**

## Project Structure

```
WorkBuddyPython/
  main.py                # Entry point
  /ui/                   # PyQt6 UI components (overlay, dialogs)
  /core/                 # Core logic (memory, notifications, scheduler, settings)
  /integrations/         # Integrations (github, calendar)
  /assets/               # Icons, images
  /tests/                # Pytest-based tests
  requirements.txt       # Dependencies
  setup.py               # Packaging/build
  README.md              # This file
```

## Development Best Practices (Cursor Rules)

- All modules must have type annotations and PEP 257-compliant docstrings.
- Use modular design: separate UI, core logic, and integrations.
- All API calls must use robust error handling and timeouts.
- Store all secrets in environment variables or config files (never hardcoded).
- All user-facing strings in `strings.py` or a localization file.
- All features must be toggleable via settings or config.
- All code must pass `flake8` and be formatted with `black`.
- All tests must use `pytest` and be in `/tests`.
- All errors must be logged with context.
- All sensitive data must be stored securely and never logged.

## Getting Started

1. Install Python 3.10+
2. Install dependencies: `pip install -r requirements.txt`
3. Run: `python main.py`

## Packaging

- Use `pyinstaller` to build a Windows executable.
- See `setup.py` for build instructions.

## Contributing

See the [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Installation

1. Make sure you have Python 3.8+ installed
2. Clone this repository 
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Setup

1. Set up your API token (optional):
   - A default Trimble API token is included
   - You can set a custom token with the environment variable: `TRIMBLE_API_TOKEN=your_token_here`

2. Generate the application icon:
   ```
   python create_icon.py
   ```

3. Configure the application to start on boot (optional):
   ```
   python setup_startup.py --enable
   ```

## Usage

### Starting the application

Run the application with:
```
python main.py
```

This will:
1. Show the WorkBuddy chat interface
2. Add a tray icon to your system tray

### Interacting with WorkBuddy

- **Text Input**: Type your questions or commands in the text field and press Enter or click Send
- **Voice Input**: Click the microphone icon and speak your command

### Sample Commands

- "Hello" - Basic greeting
- "What can you do?" - Get information about capabilities  
- "Open Firefox" - Open applications (when configured)
- "Search for [topic]" - Perform web searches (when configured)
- "Tell me about [topic]" - Ask for information

### System Tray

- **Left-click**: Open the WorkBuddy chat interface
- **Right-click**: Access menu options (Open, Quit)

## Customization

You can customize the appearance and behavior by modifying the following files:

- `main.py` - Main application logic and UI
- `ai_client.py` - AI response generation and commands
- `.taskmasterconfig` - Task definitions and configuration

## Future Enhancements

- GitHub integration for developers
- File and folder management
- Calendar and meeting management
- Email integration
- Custom voice and personalization options

## Troubleshooting

- **Speech recognition issues**: Make sure your microphone is working correctly and that you have an internet connection for Google's speech recognition service
- **Missing API responses**: Check your internet connection and that the Trimble API is accessible
- **Startup problems**: Run `setup_startup.py --disable` and then `setup_startup.py --enable` again

## License

MIT

## Credits

Created for workplace productivity enhancement. 