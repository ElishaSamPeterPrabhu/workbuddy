"""
Quick test script to verify Google APIs are working correctly.
Run this after following the API_SETUP_GUIDE.md
"""

import os
import sys
from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Required scopes for WorkBuddy
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

def authenticate_google_apis():
    """Authenticate with Google APIs and return credentials."""
    creds = None
    token_path = 'token.json'
    credentials_path = os.path.join('integrations', 'credentials.json')
    
    print("🔐 Starting Google API authentication...")
    
    # Check if credentials.json exists
    if not os.path.exists(credentials_path):
        print(f"❌ Error: {credentials_path} not found!")
        print("   Please follow the API_SETUP_GUIDE.md to get your credentials.json file")
        return None
    
    # Load existing token if available
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
        print("📄 Found existing token.json")
    
    # If no valid credentials, get new ones
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing expired token...")
            creds.refresh(Request())
        else:
            print("🌐 Opening browser for authentication...")
            print("   Please authorize WorkBuddy in your browser")
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        print("💾 Saved authentication token")
    
    return creds

def test_gmail_api(creds):
    """Test Gmail API functionality."""
    print("\n📧 Testing Gmail API...")
    try:
        service = build('gmail', 'v1', credentials=creds)
        
        # Test: Get user profile
        profile = service.users().getProfile(userId='me').execute()
        print(f"   ✅ Connected to Gmail: {profile['emailAddress']}")
        
        # Test: Get recent messages
        results = service.users().messages().list(
            userId='me', 
            maxResults=5,
            q='in:inbox'
        ).execute()
        
        messages = results.get('messages', [])
        print(f"   ✅ Can access messages: {len(messages)} recent emails found")
        
        # Test: Get unread count
        unread_results = service.users().messages().list(
            userId='me',
            q='is:unread in:inbox'
        ).execute()
        
        unread_count = len(unread_results.get('messages', []))
        print(f"   ✅ Unread emails: {unread_count}")
        
        return True
        
    except HttpError as error:
        print(f"   ❌ Gmail API error: {error}")
        return False
    except Exception as error:
        print(f"   ❌ Unexpected Gmail error: {error}")
        return False

def test_calendar_api(creds):
    """Test Google Calendar API functionality."""
    print("\n📅 Testing Calendar API...")
    try:
        service = build('calendar', 'v3', credentials=creds)
        
        # Test: Get calendar list
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        primary_calendar = next((cal for cal in calendars if cal.get('primary')), None)
        
        if primary_calendar:
            print(f"   ✅ Connected to Calendar: {primary_calendar['summary']}")
        
        # Test: Get today's events
        from datetime import datetime, timedelta
        now = datetime.utcnow().isoformat() + 'Z'
        end_of_day = (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=now,
            timeMax=end_of_day,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        print(f"   ✅ Can access events: {len(events)} events today")
        
        if events:
            for event in events[:3]:  # Show first 3 events
                start = event['start'].get('dateTime', event['start'].get('date'))
                print(f"      • {event['summary']} at {start}")
        
        return True
        
    except HttpError as error:
        print(f"   ❌ Calendar API error: {error}")
        return False
    except Exception as error:
        print(f"   ❌ Unexpected Calendar error: {error}")
        return False

def test_integration_with_workbuddy():
    """Test that WorkBuddy can use the APIs."""
    print("\n🤖 Testing WorkBuddy Integration...")
    try:
        # Import WorkBuddy components
        sys.path.append(str(Path(__file__).parent))
        from integrations.gmail import GmailIntegration
        from integrations.calendar import GoogleCalendarIntegration
        
        # Test Gmail integration
        print("   Testing Gmail integration...")
        gmail = GmailIntegration()
        email_summary = gmail.get_morning_email_summary()
        print(f"   ✅ Gmail integration: {email_summary['unread_count']} unread emails")
        
        # Test Calendar integration  
        print("   Testing Calendar integration...")
        calendar = GoogleCalendarIntegration()
        if calendar.authenticate():
            events = calendar.get_events()
            print(f"   ✅ Calendar integration: {len(events)} events today")
        
        return True
        
    except ImportError as error:
        print(f"   ❌ WorkBuddy import error: {error}")
        print("   Make sure you're running this from the workbuddy directory")
        return False
    except Exception as error:
        print(f"   ❌ Integration test error: {error}")
        return False

def main():
    """Main test function."""
    print("🚀 WorkBuddy Google APIs Test")
    print("=" * 50)
    
    # Step 1: Authenticate
    creds = authenticate_google_apis()
    if not creds:
        print("\n❌ Authentication failed!")
        print("Please check the API_SETUP_GUIDE.md and try again.")
        return False
    
    print("✅ Authentication successful!")
    
    # Step 2: Test APIs
    gmail_ok = test_gmail_api(creds)
    calendar_ok = test_calendar_api(creds)
    
    # Step 3: Test WorkBuddy integration
    workbuddy_ok = test_integration_with_workbuddy()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    print(f"Gmail API: {'✅ Working' if gmail_ok else '❌ Failed'}")
    print(f"Calendar API: {'✅ Working' if calendar_ok else '❌ Failed'}")
    print(f"WorkBuddy Integration: {'✅ Working' if workbuddy_ok else '❌ Failed'}")
    
    if gmail_ok and calendar_ok and workbuddy_ok:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 You're ready to implement the enhanced features!")
        print("\nNext steps:")
        print("1. Review the ENHANCED_INTEGRATION_PLAN.md")
        print("2. Start implementing the enhanced email and calendar features")
        print("3. Test the AI-powered morning briefing")
        return True
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")
        print("Refer to API_SETUP_GUIDE.md for troubleshooting.")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
