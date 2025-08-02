# Setting Up Google APIs for WorkBuddy

This guide will help you set up Google Calendar and Gmail integration for your Jarvis-like WorkBuddy assistant.

## Prerequisites

- A Google account
- Python 3.8+ installed
- WorkBuddy project set up

## Step 1: Enable Google APIs

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Click on "Enable APIs and Services"
4. Search for and enable:
   - **Google Calendar API**
   - **Gmail API**

## Step 2: Create OAuth 2.0 Credentials

1. In the Cloud Console, go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - Choose "External" for testing
   - Fill in the required fields (app name, user support email)
   - Add your email to test users
   - Add scopes:
     - `https://www.googleapis.com/auth/gmail.readonly`
     - `https://www.googleapis.com/auth/gmail.modify`
     - `https://www.googleapis.com/auth/calendar.readonly`
     - `https://www.googleapis.com/auth/calendar.events`

4. Create OAuth client ID:
   - Application type: "Desktop app"
   - Name: "WorkBuddy Assistant"

5. Download the credentials JSON file
6. Rename it to `credentials.json`
7. Place it in the `integrations/` directory

## Step 3: First-Time Authentication

When you run WorkBuddy for the first time with Google integrations:

1. A browser window will open
2. Log in with your Google account
3. Grant the requested permissions
4. The authentication tokens will be saved locally

## Step 4: (Optional) Weather API Setup

For weather updates in your morning briefing:

1. Sign up for a free account at [OpenWeatherMap](https://openweathermap.org/api)
2. Get your API key
3. Add to your `.env` file:
   ```
   OPENWEATHER_API_KEY=your_api_key_here
   ```

## Step 5: Configure Morning Briefing

You can customize the morning briefing by modifying these preferences in your code:

```python
from core.storage import set_user_preference

# Enable/disable morning briefing
set_user_preference('morning_briefing_enabled', True)

# Set briefing time window (24-hour format)
set_user_preference('briefing_start_hour', 7)  # 7 AM
set_user_preference('briefing_end_hour', 10)   # 10 AM

# Set weather location
set_user_preference('weather_city', 'New York')
```

## Step 6: Auto-Start Configuration

To have WorkBuddy start when your computer boots:

```bash
python setup_startup.py --enable
```

To disable auto-start:

```bash
python setup_startup.py --disable
```

## Troubleshooting

### "Credentials file not found"
- Make sure `credentials.json` is in the `integrations/` directory
- Check file permissions

### "Access blocked: This app's request is invalid"
- Make sure you've added your email to test users in Google Cloud Console
- Verify all required scopes are added

### Gmail not showing emails
- Check that Gmail API is enabled
- Verify the scopes include Gmail permissions
- Try re-authenticating by deleting `gmail_token.pickle`

### Calendar events not showing
- Ensure Calendar API is enabled
- Check that you have events in your primary calendar
- Try re-authenticating by deleting `token.pickle`

## Security Notes

- Keep your `credentials.json` file secure
- Don't commit credentials or tokens to version control
- Add these to your `.gitignore`:
  ```
  integrations/credentials.json
  integrations/token.pickle
  integrations/gmail_token.pickle
  .env
  ```

## Testing the Integration

Run this test script to verify everything is working:

```python
# test_integrations.py
from integrations.gmail import GmailIntegration
from integrations.calendar import GoogleCalendarIntegration

# Test Gmail
try:
    gmail = GmailIntegration()
    emails = gmail.get_unread_emails(max_results=3)
    print(f"Found {len(emails)} unread emails")
except Exception as e:
    print(f"Gmail error: {e}")

# Test Calendar
try:
    calendar = GoogleCalendarIntegration()
    events = calendar.get_upcoming_events(max_results=3)
    print(f"Found {len(events)} upcoming events")
except Exception as e:
    print(f"Calendar error: {e}")
```

## Next Steps

Once everything is set up:

1. WorkBuddy will greet you with a morning briefing between 7-10 AM
2. You can ask about your emails: "Check my emails"
3. You can ask about your calendar: "What's on my calendar today?"
4. Set reminders that persist across restarts
5. Get notified about important emails and meetings

Enjoy your Jarvis-like assistant experience! 