"""
Minimal OAuth test with just one scope to isolate the issue
"""

import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Test with just ONE scope first
MINIMAL_SCOPE = ['https://www.googleapis.com/auth/calendar.readonly']

def test_minimal_oauth():
    """Test OAuth with minimal scope"""
    print("🧪 MINIMAL OAUTH TEST")
    print("=" * 30)
    print("Testing with ONLY calendar.readonly scope")
    print("This helps isolate if it's a scope or config issue")
    
    creds = None
    token_path = 'minimal_token.json'
    credentials_path = 'integrations/credentials.json'
    
    # Check if we already have a token
    if os.path.exists(token_path):
        print("📄 Found existing minimal token, removing it...")
        os.remove(token_path)
    
    try:
        print("🔐 Starting minimal OAuth flow...")
        flow = InstalledAppFlow.from_client_secrets_file(
            credentials_path, MINIMAL_SCOPE)
        
        # Try to run with a different port
        print("🌐 Opening browser for minimal auth...")
        creds = flow.run_local_server(port=8080)
        
        # Save the token
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
        
        print("✅ MINIMAL AUTH SUCCESS!")
        print(f"   Token saved to: {token_path}")
        print(f"   Valid: {creds.valid}")
        print(f"   Expired: {creds.expired}")
        
        # Try to use the credentials
        from googleapiclient.discovery import build
        service = build('calendar', 'v3', credentials=creds)
        
        # Just try to get calendar list (minimal test)
        calendar_list = service.calendarList().list().execute()
        calendars = calendar_list.get('items', [])
        
        print(f"✅ API CALL SUCCESS!")
        print(f"   Found {len(calendars)} calendars")
        
        if calendars:
            for cal in calendars[:2]:  # Show first 2
                print(f"   - {cal.get('summary', 'Unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ MINIMAL AUTH FAILED: {e}")
        return False

def main():
    success = test_minimal_oauth()
    
    if success:
        print("\n🎉 GREAT NEWS!")
        print("Minimal OAuth is working!")
        print("The issue might be with:")
        print("- Too many scopes at once")
        print("- gmail.modify scope specifically") 
        print("- Some other scope-related issue")
        print("\nNext: Try adding one scope at a time")
    else:
        print("\n💔 Even minimal OAuth failed")
        print("This means the issue is fundamental:")
        print("- OAuth consent screen not properly configured")
        print("- Test user not properly added")  
        print("- App not published")
        print("- Browser cache issue")

if __name__ == '__main__':
    main()
