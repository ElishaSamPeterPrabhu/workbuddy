"""
Simple test to check Google OAuth setup without full API calls
"""

import os
import json
from pathlib import Path

def check_credentials_file():
    """Check if credentials.json exists and is valid"""
    creds_path = "integrations/credentials.json"
    
    print("🔍 Checking credentials.json file...")
    
    if not os.path.exists(creds_path):
        print("❌ credentials.json not found!")
        return False
    
    try:
        with open(creds_path, 'r') as f:
            creds_data = json.load(f)
        
        # Check if it has the right structure
        if "installed" in creds_data:
            client_data = creds_data["installed"]
            print(f"✅ Found OAuth client config")
            print(f"   Client ID: {client_data.get('client_id', 'Missing')[:20]}...")
            print(f"   Project ID: {client_data.get('project_id', 'Missing')}")
            return True
        else:
            print("❌ Invalid credentials.json format")
            return False
            
    except Exception as e:
        print(f"❌ Error reading credentials.json: {e}")
        return False

def main():
    print("🚀 Simple OAuth Configuration Test")
    print("=" * 40)
    
    # Check credentials file
    creds_ok = check_credentials_file()
    
    if not creds_ok:
        print("\n💡 Next steps:")
        print("1. Make sure credentials.json is in integrations/ folder")
        print("2. Download it again from Google Cloud Console if needed")
        return False
    
    print("\n✅ Credentials file looks good!")
    print("\n💡 Next steps to fix the 'Access blocked' error:")
    print("1. Go to Google Cloud Console")
    print("2. Go to 'APIs & Services' → 'OAuth consent screen'")
    print("3. Add your email as a test user: elrey00017@gmail.com")
    print("4. Make sure these scopes are added:")
    print("   - gmail.readonly")
    print("   - gmail.modify") 
    print("   - calendar.readonly")
    print("   - calendar.events")
    print("5. Try the authentication again")
    
    return True

if __name__ == '__main__':
    main()
