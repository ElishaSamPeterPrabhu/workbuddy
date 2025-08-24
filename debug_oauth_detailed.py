"""
Detailed OAuth debugging script to identify the exact issue
"""

import json
import os

def check_oauth_consent_status():
    """Print exact steps to verify OAuth consent screen"""
    print("🔍 DETAILED OAUTH CONSENT SCREEN CHECK")
    print("=" * 50)
    
    print("1. Go to: https://console.cloud.google.com/apis/credentials/consent")
    print("2. In the top bar, make sure you see: 'windows-470002'")
    print("3. Check the following sections:")
    
    print("\n📋 APP INFORMATION:")
    print("   - App name: Should say 'WorkBuddy Assistant' or similar")
    print("   - User support email: Should be filled")
    
    print("\n📋 PUBLISHING STATUS:")
    print("   Look for these exact options:")
    print("   - [ ] Testing (needs test users)")
    print("   - [ ] In production (published)")
    print("   CURRENT STATUS: _____________")
    
    print("\n📋 USER TYPE:")
    print("   - [ ] Internal (Google Workspace only)")  
    print("   - [ ] External (any Google user)")
    print("   CURRENT TYPE: _____________")
    
    print("\n📋 SCOPES SECTION:")
    print("   Should show 4 scopes:")
    print("   - [ ] gmail.readonly")
    print("   - [ ] gmail.modify")
    print("   - [ ] calendar.readonly") 
    print("   - [ ] calendar.events")
    
    print("\n📋 TEST USERS SECTION:")
    print("   Should show: elrey00017@gmail.com")
    print("   CURRENTLY SHOWS: _____________")

def alternative_solutions():
    """Provide alternative solutions"""
    print("\n🛠️ ALTERNATIVE SOLUTIONS")
    print("=" * 50)
    
    print("\n💡 SOLUTION 1: Create New Project")
    print("Sometimes OAuth consent gets corrupted. Try:")
    print("1. Create a completely new Google Cloud project")
    print("2. Enable Gmail + Calendar APIs") 
    print("3. Create new OAuth credentials")
    print("4. Download new credentials.json")
    
    print("\n💡 SOLUTION 2: Use Service Account (No OAuth)")
    print("1. Create Service Account instead of OAuth")
    print("2. Download service account JSON key")
    print("3. Use domain-wide delegation")
    print("4. No browser authorization needed")
    
    print("\n💡 SOLUTION 3: Clear Browser Cache")
    print("1. Clear all cookies for accounts.google.com")
    print("2. Use incognito/private browser window")
    print("3. Try different browser entirely")
    
    print("\n💡 SOLUTION 4: Check Project Quotas")
    print("1. Go to: https://console.cloud.google.com/iam-admin/quotas")
    print("2. Search for 'Gmail API' and 'Calendar API'")
    print("3. Make sure quotas are not exceeded")

def create_new_credentials_guide():
    """Guide for creating fresh credentials"""
    print("\n📋 FRESH CREDENTIALS SETUP")
    print("=" * 50)
    
    print("If nothing else works, let's start fresh:")
    print("\n1. Delete current credentials:")
    print("   rm integrations/credentials.json")
    print("   rm token.json")
    
    print("\n2. Create new Google Cloud project:")
    print("   - Go to: https://console.cloud.google.com/")
    print("   - New Project → 'WorkBuddy-Fresh'")
    
    print("\n3. Enable APIs in new project:")
    print("   - Gmail API")
    print("   - Calendar API")
    
    print("\n4. Configure OAuth consent (External, Published):")
    print("   - Add your email as test user")
    print("   - Add all 4 scopes")
    print("   - Immediately publish the app")
    
    print("\n5. Create new OAuth credentials:")
    print("   - Desktop application")
    print("   - Download JSON → rename to credentials.json")

def check_current_setup():
    """Check what we currently have"""
    print("\n📊 CURRENT SETUP STATUS")
    print("=" * 50)
    
    creds_path = "integrations/credentials.json"
    
    if os.path.exists(creds_path):
        try:
            with open(creds_path) as f:
                creds = json.load(f)
            
            project_id = creds["installed"]["project_id"]
            client_id = creds["installed"]["client_id"]
            
            print(f"✅ Credentials file exists")
            print(f"   Project ID: {project_id}")
            print(f"   Client ID: {client_id[:30]}...")
            
            # Check if token exists
            if os.path.exists("token.json"):
                print(f"⚠️  Old token.json exists (may cause conflicts)")
                print("   Consider deleting it: rm token.json")
            else:
                print(f"✅ No conflicting token file")
                
        except Exception as e:
            print(f"❌ Error reading credentials: {e}")
    else:
        print(f"❌ No credentials.json found")

def main():
    check_current_setup()
    check_oauth_consent_status()
    alternative_solutions() 
    create_new_credentials_guide()
    
    print("\n" + "=" * 50)
    print("🎯 IMMEDIATE ACTION ITEMS:")
    print("1. Check OAuth consent screen status (copy the checklist above)")
    print("2. If still blocked, try SOLUTION 3 (clear browser cache)")
    print("3. If still blocked, try SOLUTION 1 (new project)")
    print("=" * 50)

if __name__ == '__main__':
    main()
