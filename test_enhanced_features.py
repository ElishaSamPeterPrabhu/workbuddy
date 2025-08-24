"""
Test script for enhanced Gmail and Calendar features with AI integration.
"""

import sys
import os
import json
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_email_collector():
    """Test the enhanced email collector."""
    print("🧪 Testing Enhanced Email Collector")
    print("=" * 50)
    
    try:
        from core.enhanced_email_collector import EnhancedEmailCollector
        
        collector = EnhancedEmailCollector()
        
        if not collector.initialized:
            print("❌ Email collector failed to initialize")
            return False
        
        print("✅ Email collector initialized")
        
        # Test email collection
        print("📧 Collecting emails with context...")
        emails = collector.collect_emails_with_context(hours_back=24)
        print(f"   Collected {len(emails)} emails")
        
        if emails:
            sample_email = emails[0]
            print("📋 Sample email analysis:")
            print(f"   Subject: {sample_email.get('subject', 'No subject')}")
            print(f"   Sender importance: {sample_email.get('sender_importance', 'Unknown')}/10")
            print(f"   Urgency score: {sample_email.get('urgency_score', 'Unknown')}/10")
            print(f"   Email type: {sample_email.get('email_type', 'Unknown')}")
            print(f"   Meeting detection: {sample_email.get('meeting_detection', {}).get('is_meeting_related', False)}")
        
        # Test categorization
        print("📂 Categorizing emails for AI...")
        categorized = collector.categorize_emails_for_ai(emails)
        
        print("📊 Email categories:")
        for category, email_list in categorized.items():
            print(f"   {category}: {len(email_list)} emails")
        
        # Test summary data
        print("📈 Generating summary data...")
        summary_data = collector.get_email_summary_data()
        print(f"   Total emails: {summary_data.get('total_emails', 0)}")
        print(f"   Top senders: {len(summary_data.get('top_senders', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced email collector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_calendar_collector():
    """Test the enhanced calendar collector."""
    print("\n🧪 Testing Enhanced Calendar Collector")
    print("=" * 50)
    
    try:
        from core.enhanced_calendar_collector import EnhancedCalendarCollector
        
        collector = EnhancedCalendarCollector()
        
        if not collector.initialized:
            print("❌ Calendar collector failed to initialize")
            return False
        
        print("✅ Calendar collector initialized")
        
        # Test calendar collection
        print("📅 Collecting meetings with prep data...")
        events = collector.collect_meetings_with_prep_data(days_ahead=7)
        print(f"   Collected {len(events)} events")
        
        if events:
            sample_event = events[0]
            print("📋 Sample event analysis:")
            print(f"   Summary: {sample_event.get('summary', 'No summary')}")
            print(f"   Meeting type: {sample_event.get('meeting_analysis', {}).get('type', 'Unknown')}")
            print(f"   Importance score: {sample_event.get('importance_score', 'Unknown')}/10")
            print(f"   Prep level: {sample_event.get('preparation_required', {}).get('level', 'Unknown')}")
            print(f"   Attendee count: {sample_event.get('attendee_context', {}).get('count', 0)}")
            
            # Show agenda items if available
            agenda = sample_event.get('agenda_items', [])
            if agenda:
                print(f"   Agenda items: {', '.join(agenda[:2])}")
        
        # Test summary data
        print("📈 Generating calendar summary...")
        summary_data = collector.get_calendar_summary_data()
        print(f"   Today's events: {len(summary_data.get('today_events', []))}")
        print(f"   Events needing prep: {len(summary_data.get('meetings_needing_prep', []))}")
        print(f"   High importance: {len(summary_data.get('high_importance_meetings', []))}")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced calendar collector test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_intelligence_engine():
    """Test the AI intelligence engine."""
    print("\n🧪 Testing AI Intelligence Engine")
    print("=" * 50)
    
    try:
        from core.ai_intelligence_engine import AIIntelligenceEngine
        
        ai_engine = AIIntelligenceEngine()
        print(f"✅ AI engine initialized (AI client available: {ai_engine.initialized})")
        
        # Create sample data for testing
        sample_email_data = {
            'total_emails': 10,
            'categories': {
                'urgent_action_required': [
                    {'subject': 'Urgent: Project deadline tomorrow', 'sender': 'manager@company.com'}
                ],
                'meeting_related': [
                    {'subject': 'Meeting invitation: Weekly standup', 'sender': 'team@company.com'}
                ],
                'informational': []
            },
            'top_senders': [{'sender': 'manager@company.com', 'count': 3, 'importance': 8}]
        }
        
        sample_calendar_data = {
            'total_events': 3,
            'today_events': [
                {'summary': 'Team Meeting', 'importance_score': 6},
                {'summary': 'Client Call', 'importance_score': 8}
            ],
            'meetings_needing_prep': [
                {'summary': 'Client Presentation', 'preparation_required': {'level': 'high'}}
            ]
        }
        
        # Test email intelligence
        print("📧 Testing email intelligence...")
        email_intelligence = ai_engine.generate_email_intelligence(sample_email_data)
        print(f"   Generated summary: {len(email_intelligence.get('summary', ''))} characters")
        print(f"   Source: {email_intelligence.get('source', 'unknown')}")
        if email_intelligence.get('summary'):
            print(f"   Preview: {email_intelligence['summary'][:100]}...")
        
        # Test calendar intelligence
        print("📅 Testing calendar intelligence...")
        calendar_intelligence = ai_engine.generate_calendar_intelligence(sample_calendar_data)
        print(f"   Generated summary: {len(calendar_intelligence.get('summary', ''))} characters")
        print(f"   Source: {calendar_intelligence.get('source', 'unknown')}")
        if calendar_intelligence.get('summary'):
            print(f"   Preview: {calendar_intelligence['summary'][:100]}...")
        
        # Test daily briefing
        print("📋 Testing daily briefing generation...")
        daily_briefing = ai_engine.generate_daily_briefing(sample_email_data, sample_calendar_data)
        print(f"   Generated briefing: {len(daily_briefing.get('briefing_text', ''))} characters")
        print(f"   Source: {daily_briefing.get('source', 'unknown')}")
        if daily_briefing.get('briefing_text'):
            print(f"   Preview: {daily_briefing['briefing_text'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI intelligence engine test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_morning_briefing():
    """Test the enhanced morning briefing system."""
    print("\n🧪 Testing Enhanced Morning Briefing")
    print("=" * 50)
    
    try:
        from core.enhanced_morning_briefing import EnhancedMorningBriefing
        
        briefing_system = EnhancedMorningBriefing()
        print("✅ Enhanced morning briefing system initialized")
        
        # Test briefing summary (quick preview)
        print("📊 Getting briefing summary...")
        summary = briefing_system.get_briefing_summary()
        
        if 'error' not in summary:
            print("📈 Briefing data available:")
            email_counts = summary.get('email_counts', {})
            calendar_counts = summary.get('calendar_counts', {})
            
            print(f"   Email categories: {email_counts}")
            print(f"   Calendar events: {calendar_counts}")
            print(f"   Weather available: {summary.get('weather_available', False)}")
            print(f"   Reminders: {summary.get('reminders_count', 0)}")
            print(f"   Estimated time: {summary.get('estimated_briefing_time', 0)} seconds")
        
        # Test full briefing generation (this might take a moment)
        print("🎙️ Generating full enhanced briefing...")
        briefing_data = briefing_system.generate_enhanced_briefing()
        
        print("📋 Briefing generated successfully!")
        print(f"   Type: {briefing_data.get('type', 'unknown')}")
        print(f"   Word count: {briefing_data.get('word_count', 0)}")
        print(f"   Estimated speak time: {briefing_data.get('estimated_speak_time', 0):.1f} seconds")
        
        briefing_text = briefing_data.get('briefing_text', '')
        if briefing_text:
            print(f"   Preview: {briefing_text[:150]}...")
        
        # Test email priority briefing
        print("📧 Testing email priority briefing...")
        email_briefing = briefing_system.get_email_priority_briefing()
        print(f"   Email briefing type: {email_briefing.get('type', 'unknown')}")
        
        if email_briefing.get('type') != 'error':
            print(f"   Total emails: {email_briefing.get('total_count', 0)}")
            print(f"   Urgent emails: {email_briefing.get('urgent_count', 0)}")
        
        # Test meeting preparation briefing
        print("📅 Testing meeting preparation briefing...")
        meeting_briefing = briefing_system.get_meeting_preparation_briefing()
        print(f"   Meeting briefing type: {meeting_briefing.get('type', 'unknown')}")
        
        if meeting_briefing.get('type') == 'meeting_preparation':
            print(f"   Meeting: {meeting_briefing.get('meeting_summary', 'Unknown')}")
            print(f"   Prep time: {meeting_briefing.get('estimated_prep_time', 0)} minutes")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced morning briefing test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_workbuddy():
    """Test integration with existing WorkBuddy systems."""
    print("\n🧪 Testing WorkBuddy Integration")
    print("=" * 50)
    
    try:
        # Test that we can import existing components
        from integrations.gmail import GmailIntegration
        from integrations.calendar import GoogleCalendarIntegration
        from core.ai_client import AIClient
        
        print("✅ Successfully imported existing WorkBuddy components")
        
        # Test that existing systems still work
        gmail = GmailIntegration()
        print(f"✅ Gmail integration available: {gmail is not None}")
        
        calendar = GoogleCalendarIntegration()
        print(f"✅ Calendar integration available: {calendar is not None}")
        
        ai_client = AIClient()
        print(f"✅ AI client available: {ai_client is not None}")
        
        # Test compatibility
        print("🔗 Testing backward compatibility...")
        
        # This should still work (original morning briefing)
        from core.morning_briefing import MorningBriefing
        original_briefing = MorningBriefing()
        original_text = original_briefing.generate_morning_briefing()
        print(f"✅ Original briefing still works: {len(original_text)} characters")
        
        return True
        
    except Exception as e:
        print(f"❌ WorkBuddy integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all enhanced feature tests."""
    print("🚀 WorkBuddy Enhanced Features Test Suite")
    print("=" * 60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_results = []
    
    # Run all tests
    tests = [
        ("Enhanced Email Collector", test_enhanced_email_collector),
        ("Enhanced Calendar Collector", test_enhanced_calendar_collector),
        ("AI Intelligence Engine", test_ai_intelligence_engine),
        ("Enhanced Morning Briefing", test_enhanced_morning_briefing),
        ("WorkBuddy Integration", test_integration_with_workbuddy)
    ]
    
    for test_name, test_function in tests:
        try:
            result = test_function()
            test_results.append((test_name, result))
        except Exception as e:
            print(f"💥 Test '{test_name}' crashed: {e}")
            test_results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\nTotal: {len(test_results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        print("🚀 Your enhanced WorkBuddy features are ready!")
        print("\nNext steps:")
        print("1. Try running: python -c \"from core.enhanced_morning_briefing import EnhancedMorningBriefing; briefing = EnhancedMorningBriefing(); print(briefing.generate_enhanced_briefing()['briefing_text'])\"")
        print("2. Integrate with main WorkBuddy application")
        print("3. Set up automated morning briefings")
    else:
        print(f"\n⚠️  {failed} test(s) failed. Please check the errors above.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    return failed == 0

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
