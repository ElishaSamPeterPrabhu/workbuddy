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
  /ui/                   # PyQt6 UI components (overlay, tray)
  /core/                 # Core logic (ai_client, file search, storage, notifications, scheduler)
  /integrations/         # Integrations (github, calendar)
  /assets/               # Icons, images
  /tests/                # Pytest-based tests
  /config/               # Configuration files
  requirements.txt       # Dependencies
  setup.py               # Packaging/build
  setup_startup.py       # Configure autostart
  run_workbuddy.bat      # Windows batch file to run the app
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

- `main.py` - Main application logic
- `ui/overlay.py` - Chat UI and appearance
- `ui/tray.py` - System tray integration
- `core/ai_client.py` - AI response generation and commands
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

# WorkBuddy File Search

This project implements an advanced file search system for the WorkBuddy assistant, powered by the Everything SDK.

## Features

- **Natural Language File Search**: Ask for files in plain English
- **Lightning-Fast Results**: Uses Everything SDK for near-instant file search
- **Advanced Filtering**: Search by file type, size, date modified, and more
- **AI Integration**: Seamlessly connects with AI assistant workflows
- **Graceful Fallback**: Falls back to standard file system search if Everything isn't installed

## Dependencies

- Python 3.8+
- `pyeverything` - Python wrapper for the Everything SDK
- Everything Search Engine - Free utility from voidtools (https://www.voidtools.com/)

## Installation

1. Install the Everything Search Engine from https://www.voidtools.com/
2. Install the Python dependencies:

```bash
pip install pyeverything
```

## Usage

### Command Line Testing

You can test the file search functionality using the included test scripts:

```bash
# Show example queries
python -m tests.test_file_search --examples

# Search using natural language
python -m tests.test_file_search --query "Find PDF files in Documents"

# Use a JSON command
python -m tests.test_file_search --command '{"action": "list_files", "directory": "C:/Users/username/Desktop", "pattern": "*.txt"}'

# Compare search methods
python -m tests.test_compare_search_methods --examples

# Test prioritized search
python -m tests.test_search_navigator --examples

# Interactive file search testing
python -m tests.test_real_file_search
```

### Integration with AI Assistant

The file search system is designed to integrate with AI workflows:

```python
from core.ai_file_search_handler import file_search_handler

# Process a natural language query
response = file_search_handler.natural_language_search("Find Excel files created last week")
print(response)

# Process a command from the AI
command = {
    "action": "search_files_recursive",
    "directory": "C:/Users/username/Documents",
    "pattern": "*.pdf"
}
results = file_search_handler.process_ai_command(command)
```

## Architecture

The system consists of three main components:

1. **EverythingSearch** (`everything_search.py`) - Wrapper for the Everything SDK
2. **FileSearchAdapter** (`file_search_adapter.py`) - Translates queries to search parameters
3. **AIFileSearchHandler** (`ai_file_search_handler.py`) - Handles AI integration

## Example Queries

The system understands a wide range of natural language queries:

- "Find PDF files in Documents"
- "Show me text files on my Desktop"
- "Find files larger than 10MB"
- "Search for files modified today"
- "Look for files with 'report' in the name"
- "Show me images from last week"
- "Find Excel files in Downloads"

## Supported Commands

The system supports the following JSON commands:

```json
{"action": "list_folders", "directory": "C:/Path/To/Directory"}
{"action": "list_files", "directory": "C:/Path/To/Directory", "pattern": "*.txt"}
{"action": "search_files_recursive", "directory": "C:/Path/To/Directory", "pattern": "*.pdf"}
{"action": "file_exists", "path": "C:/Path/To/File.txt"}
{"action": "folder_exists", "path": "C:/Path/To/Folder"}
{"action": "process_query", "query": "Find large files in Documents"}
```

## Notes

- Everything SDK must be installed and running for optimal performance
- The system will fall back to standard file system search if Everything is not available
- Content search requires Everything with content indexing enabled 