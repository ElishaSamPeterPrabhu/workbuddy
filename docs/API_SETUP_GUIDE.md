# Google APIs Setup Guide for WorkBuddy Enhanced Integration

## 🚀 Quick Setup Overview

You need to get **Google API credentials** to access Gmail and Calendar data. Here's exactly what to do:

## Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Click "New Project"** (top-left, next to "Google Cloud")
3. **Name your project**: "WorkBuddy Assistant" 
4. **Click "Create"**

## Step 2: Enable Required APIs

Once your project is created:

1. **Go to "APIs & Services" → "Library"** (from left sidebar)
2. **Search and Enable these APIs**:
   - **Gmail API** - Click "Enable"
   - **Google Calendar API** - Click "Enable"

## Step 3: Create OAuth 2.0 Credentials

### Configure OAuth Consent Screen First:
1. **Go to "APIs & Services" → "OAuth consent screen"**
2. **Choose "External"** (for testing)
3. **Fill required fields**:
   - App name: `WorkBuddy Assistant`
   - User support email: `your-email@gmail.com`
   - Developer contact: `your-email@gmail.com`
4. **Click "Save and Continue"**

### Add Scopes:
1. **Click "Add or Remove Scopes"**
2. **Add these scopes**:
   ```
   https://www.googleapis.com/auth/gmail.readonly
   https://www.googleapis.com/auth/gmail.modify
   https://www.googleapis.com/auth/calendar.readonly
   https://www.googleapis.com/auth/calendar.events
   ```
3. **Click "Save and Continue"**

### Add Test Users:
1. **Add your email** as a test user
2. **Click "Save and Continue"**

### Create Credentials:
1. **Go to "APIs & Services" → "Credentials"**
2. **Click "Create Credentials" → "OAuth client ID"**
3. **Choose "Desktop application"**
4. **Name**: "WorkBuddy Desktop"
5. **Click "Create"**
6. **Download the JSON file** (this is your `credentials.json`)

## Step 4: Install the Credentials

1. **Rename the downloaded file** to `credentials.json`
2. **Place it in your WorkBuddy project**:
   ```
   workbuddy/
   ├── integrations/
   │   └── credentials.json  ← Put it here
   ```

## Step 5: Install Required Python Libraries

```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2
pip install google-api-python-client
```

## Step 6: Test the Setup

Create a quick test file to verify everything works:

```python
# test_google_apis.py
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/calendar.readonly'
]

def test_apis():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'integrations/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    # Test Gmail API
    try:
        gmail_service = build('gmail', 'v1', credentials=creds)
        results = gmail_service.users().messages().list(userId='me', maxResults=1).execute()
        print("✅ Gmail API working!")
    except Exception as e:
        print(f"❌ Gmail API error: {e}")
    
    # Test Calendar API
    try:
        calendar_service = build('calendar', 'v3', credentials=creds)
        now = '2024-01-01T00:00:00Z'
        events_result = calendar_service.events().list(
            calendarId='primary', timeMin=now, maxResults=1).execute()
        print("✅ Calendar API working!")
    except Exception as e:
        print(f"❌ Calendar API error: {e}")

if __name__ == '__main__':
    test_apis()
```

**Run the test**:
```bash
python test_google_apis.py
```

## Step 7: Optional - Weather API

For weather in morning briefings:

1. **Go to**: https://openweathermap.org/api
2. **Sign up for free account**
3. **Get your API key**
4. **Add to your `.env` file**:
   ```
   OPENWEATHER_API_KEY=your_weather_api_key_here
   ```

## 🔒 Security Notes

1. **Never commit these files to Git**:
   - `credentials.json`
   - `token.json`
   - `.env`

2. **Add to your `.gitignore`**:
   ```
   integrations/credentials.json
   token.json
   .env
   *.pickle
   ```

## 🚨 Troubleshooting

### "Error 403: access_denied"
- Make sure you added your email to test users
- Check that all required scopes are added

### "Error 400: redirect_uri_mismatch"
- Make sure you selected "Desktop application" not "Web application"

### "FileNotFoundError: credentials.json"
- Check the file is in the `integrations/` folder
- Make sure it's named exactly `credentials.json`

## ✅ You're Ready!

Once you see "✅ Gmail API working!" and "✅ Calendar API working!", you can proceed with the WorkBuddy integration.

The first time you run WorkBuddy, it will:
1. Open a browser window
2. Ask you to authorize the app
3. Save the tokens for future use
4. Start providing Gmail and Calendar features

---

**Next Steps**: After getting APIs working, we'll integrate the enhanced features into WorkBuddy and test the AI-powered email and calendar intelligence!
