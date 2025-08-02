"""
Test script for Google Calendar and Gmail integrations.

Run this to verify your Google APIs are properly configured.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from integrations.gmail import GmailIntegration
from integrations.calendar import GoogleCalendarIntegration
from core.morning_briefing import MorningBriefing


def test_gmail():
    """Test Gmail integration."""
    print("=" * 50)
    print("Testing Gmail Integration")
    print("=" * 50)
    
    try:
        gmail = GmailIntegration()
        print("✓ Gmail authentication successful")
        
        # Test getting unread emails
        print("\nFetching unread emails...")
        emails = gmail.get_unread_emails(max_results=5)
        
        if emails:
            print(f"\nFound {len(emails)} unread emails:")
            for i, email in enumerate(emails, 1):
                sender = email['sender'].split('<')[0].strip()
                print(f"\n{i}. From: {sender}")
                print(f"   Subject: {email['subject']}")
                print(f"   Preview: {email['snippet'][:80]}...")
        else:
            print("\nNo unread emails found.")
        
        # Test getting important emails
        print("\n\nFetching important emails from last 24 hours...")
        important = gmail.get_important_emails(hours=24)
        print(f"Found {len(important)} important emails")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Gmail test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure credentials.json is in the integrations/ directory")
        print("2. Check that Gmail API is enabled in Google Cloud Console")
        print("3. Delete gmail_token.pickle and try again to re-authenticate")
        return False


def test_calendar():
    """Test Google Calendar integration."""
    print("\n" + "=" * 50)
    print("Testing Google Calendar Integration")
    print("=" * 50)
    
    try:
        calendar = GoogleCalendarIntegration()
        print("✓ Calendar authentication successful")
        
        # Test getting upcoming events
        print("\nFetching upcoming events...")
        events = calendar.get_upcoming_events(max_results=5)
        
        if events:
            print(f"\nFound {len(events)} upcoming events:")
            for i, event in enumerate(events, 1):
                print(f"\n{i}. {event['summary']}")
                print(f"   When: {event['start_time']}")
                if event.get('location'):
                    print(f"   Where: {event['location']}")
        else:
            print("\nNo upcoming events found.")
        
        # Test getting today's events
        print("\n\nFetching today's events...")
        today_events = calendar.get_todays_events()
        print(f"Found {len(today_events)} events today")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Calendar test failed: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure credentials.json is in the integrations/ directory")
        print("2. Check that Calendar API is enabled in Google Cloud Console")
        print("3. Delete token.pickle and try again to re-authenticate")
        return False


def test_morning_briefing():
    """Test morning briefing generation."""
    print("\n" + "=" * 50)
    print("Testing Morning Briefing")
    print("=" * 50)
    
    try:
        briefing = MorningBriefing()
        
        # Generate briefing text
        print("\nGenerating morning briefing...")
        briefing_text = briefing.generate_morning_briefing()
        
        print("\nMorning Briefing:")
        print("-" * 40)
        print(briefing_text)
        print("-" * 40)
        
        return True
        
    except Exception as e:
        print(f"\n✗ Morning briefing test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("WorkBuddy Google Integration Test Suite")
    print("=" * 50)
    
    # Run tests
    gmail_ok = test_gmail()
    calendar_ok = test_calendar()
    briefing_ok = test_morning_briefing()
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)
    print(f"Gmail Integration: {'✓ PASSED' if gmail_ok else '✗ FAILED'}")
    print(f"Calendar Integration: {'✓ PASSED' if calendar_ok else '✗ FAILED'}")
    print(f"Morning Briefing: {'✓ PASSED' if briefing_ok else '✗ FAILED'}")
    
    if gmail_ok and calendar_ok and briefing_ok:
        print("\n🎉 All tests passed! Your Jarvis-like assistant is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")


if __name__ == "__main__":
    main() 