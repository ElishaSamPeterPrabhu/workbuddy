"""
OAuth troubleshooting script to help debug the access_denied issue
"""

import json
import os
from urllib.parse import urlencode

def analyze_oauth_request():
    """Analyze the OAuth request parameters"""
    print("🔍 OAuth Request Analysis")
    print("=" * 40)
    
    # The request details from the error
    request_details = {
        'client_id': '656476653387-ql4r2irhjiqanndlrlrluea4lvv99smq.apps.googleusercontent.com',
        'scopes': [
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.modify', 
            'https://www.googleapis.com/auth/calendar.readonly',
            'https://www.googleapis.com/auth/calendar.events'
        ],
        'redirect_uri': 'http://localhost:57903/',
        'response_type': 'code',
        'access_type': 'offline'
    }
    
    print(f"✅ Client ID: {request_details['client_id'][:20]}...")
    print(f"✅ Scopes ({len(request_details['scopes'])}):")
    for scope in request_details['scopes']:
        print(f"   - {scope.split('/')[-1]}")
    print(f"✅ Redirect URI: {request_details['redirect_uri']}")
    
    print("\n🚨 Error 403: access_denied means:")
    print("1. ❌ Your email (elrey00017@gmail.com) is NOT in test users")
    print("2. ❌ OR the OAuth consent screen is not configured properly")
    print("3. ❌ OR there's a caching issue with Google OAuth")

def suggest_solutions():
    """Suggest solutions for the OAuth issue"""
    print("\n🛠️  SOLUTIONS TO TRY:")
    print("=" * 40)
    
    print("\n📝 OPTION 1: Verify Test User Setup")
    print("1. Go to: https://console.cloud.google.com/apis/credentials/consent")
    print("2. Select project: windows-470002") 
    print("3. Scroll to 'Test users' section")
    print("4. Verify elrey00017@gmail.com is listed")
    print("5. If not listed, click '+ ADD USERS' and add it")
    
    print("\n📝 OPTION 2: Make App Internal (if using Google Workspace)")
    print("1. In OAuth consent screen")
    print("2. Change 'User Type' from 'External' to 'Internal'")
    print("3. This bypasses the verification requirement")
    
    print("\n📝 OPTION 3: Publish App (Temporary)")
    print("1. In OAuth consent screen") 
    print("2. Click 'PUBLISH APP'")
    print("3. Confirm publishing")
    print("4. This allows any Google user to access")
    
    print("\n📝 OPTION 4: Use Different Scopes (Minimal)")
    print("1. Try with just basic scopes first:")
    print("   - gmail.readonly only")
    print("   - calendar.readonly only") 
    print("2. Add more scopes after basic auth works")

def create_minimal_test():
    """Create a minimal OAuth test with fewer scopes"""
    print("\n🧪 Creating minimal test...")
    
    minimal_scopes = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/calendar.readonly'
    ]
    
    # Create a minimal auth URL
    params = {
        'client_id': '656476653387-ql4r2irhjiqanndlrlrluea4lvv99smq.apps.googleusercontent.com',
        'redirect_uri': 'http://localhost:8080',
        'scope': ' '.join(minimal_scopes),
        'response_type': 'code',
        'access_type': 'offline',
        'state': 'minimal_test'
    }
    
    auth_url = 'https://accounts.google.com/o/oauth2/auth?' + urlencode(params)
    
    print("Try this minimal OAuth URL (copy and paste in browser):")
    print(auth_url)
    
def main():
    analyze_oauth_request()
    suggest_solutions() 
    create_minimal_test()
    
    print("\n" + "=" * 50)
    print("🎯 RECOMMENDED NEXT STEP:")
    print("1. Try OPTION 3 (Publish App) - it's the quickest fix")
    print("2. Then run the test again")
    print("=" * 50)

if __name__ == '__main__':
    main()
