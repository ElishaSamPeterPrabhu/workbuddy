"""Test the Morning Briefing feature of WorkBuddy."""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.ai_client import AIClient
from core.morning_briefing import MorningBriefingSystem
import json
from datetime import datetime

def test_ai_morning_briefing():
    """Test if AI recognizes morning briefing requests."""
    print("Testing AI Morning Briefing Recognition")
    print("=" * 60)
    
    ai_client = AIClient()
    
    # Different ways to ask for morning briefing
    queries = [
        "Give me my morning briefing",
        "What's my morning briefing?",
        "Morning briefing please",
        "Show me today's briefing",
        "Daily briefing"
    ]
    
    for query in queries:
        print(f"\nUser: {query}")
        print("-" * 40)
        
        response = ai_client.get_response(query)
        
        try:
            parsed = json.loads(response)
            action = parsed.get('action')
            ai_response = parsed.get('ai_response', '')
            
            print(f"AI Action: {action}")
            print(f"Expected: morning_briefing")
            print(f"Result: {'✓ PASS' if action == 'morning_briefing' else '✗ FAIL'}")
            print(f"AI Says: {ai_response[:100]}...")
            
        except Exception as e:
            print(f"Error: {e}")

def test_actual_morning_briefing():
    """Test the actual morning briefing system."""
    print("\n\nTesting Actual Morning Briefing System")
    print("=" * 60)
    
    try:
        # Initialize the morning briefing system
        mbs = MorningBriefingSystem()
        
        print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nGenerating morning briefing...\n")
        
        # Get the briefing
        briefing = mbs.get_morning_briefing()
        
        # Display the briefing
        print(briefing)
        
        # Also test individual components
        print("\n" + "=" * 60)
        print("Testing Individual Components:")
        print("=" * 60)
        
        # Test greeting
        print("\n1. Greeting:")
        print("-" * 40)
        greeting = mbs._generate_greeting()
        print(greeting)
        
        # Test weather (might need API key)
        print("\n2. Weather Summary:")
        print("-" * 40)
        try:
            weather = mbs._get_weather_summary()
            print(weather)
        except Exception as e:
            print(f"Weather not available: {e}")
        
        # Test reminders
        print("\n3. Today's Reminders:")
        print("-" * 40)
        reminders = mbs._get_todays_reminders()
        if reminders:
            for r in reminders:
                print(f"- {r['message']} at {r['remind_at']}")
        else:
            print("No reminders for today")
        
        # Test calendar (might need integration)
        print("\n4. Calendar Events:")
        print("-" * 40)
        try:
            events = mbs._get_calendar_events()
            if events:
                for event in events:
                    print(f"- {event}")
            else:
                print("No calendar events found")
        except Exception as e:
            print(f"Calendar not available: {e}")
        
        # Test email summary
        print("\n5. Email Summary:")
        print("-" * 40)
        try:
            email_summary = mbs._get_email_summary()
            print(email_summary)
        except Exception as e:
            print(f"Email summary not available: {e}")
        
    except Exception as e:
        print(f"Error testing morning briefing system: {e}")
        import traceback
        traceback.print_exc()

def test_with_context():
    """Test morning briefing with some context data."""
    print("\n\nTesting Morning Briefing with Context")
    print("=" * 60)
    
    ai_client = AIClient()
    
    # Provide context
    context = "I have 3 meetings today and 2 important emails to respond to."
    response = ai_client.get_response(f"{context} Can you give me my morning briefing?")
    
    try:
        parsed = json.loads(response)
        print(f"AI Action: {parsed.get('action')}")
        print(f"AI Response: {parsed.get('ai_response', '')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Test AI recognition
    test_ai_morning_briefing()
    
    # Test actual system
    test_actual_morning_briefing()
    
    # Test with context
    test_with_context()