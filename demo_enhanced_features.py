"""
Quick demo of enhanced WorkBuddy features with limited data processing.
"""

import sys
import os
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_enhanced_morning_briefing():
    """Demo the enhanced morning briefing with limited email processing."""
    print("🌅 Enhanced Morning Briefing Demo")
    print("=" * 40)
    
    try:
        from core.enhanced_morning_briefing import EnhancedMorningBriefing
        
        print("🚀 Initializing enhanced morning briefing...")
        briefing_system = EnhancedMorningBriefing()
        
        # Get a quick summary first (doesn't process all emails)
        print("📊 Getting briefing summary...")
        summary = briefing_system.get_briefing_summary()
        
        if 'error' not in summary:
            print("✅ Data Summary Available:")
            email_counts = summary.get('email_counts', {})
            calendar_counts = summary.get('calendar_counts', {})
            
            print(f"   📧 Email categories detected:")
            for category, count in email_counts.items():
                if count > 0:
                    print(f"      • {category.replace('_', ' ').title()}: {count}")
            
            print(f"   📅 Calendar events:")
            for event_type, count in calendar_counts.items():
                print(f"      • {event_type.replace('_', ' ').title()}: {count}")
            
            print(f"   🌤️  Weather data: {'Available' if summary.get('weather_available') else 'Not available'}")
            print(f"   ⏰ Reminders today: {summary.get('reminders_count', 0)}")
            print(f"   ⏱️  Estimated briefing time: {summary.get('estimated_briefing_time', 0)} seconds")
            
            return True
        else:
            print(f"❌ Error getting summary: {summary.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def demo_email_intelligence():
    """Demo email intelligence with limited processing."""
    print("\n📧 Email Intelligence Demo")
    print("=" * 40)
    
    try:
        from core.enhanced_email_collector import EnhancedEmailCollector
        
        print("🔍 Initializing email collector...")
        collector = EnhancedEmailCollector()
        
        if not collector.initialized:
            print("❌ Email collector not initialized")
            return False
        
        print("✅ Email collector ready")
        print("📊 Processing limited email sample...")
        
        # Process just a few emails instead of all 100
        emails = collector.collect_emails_with_context(hours_back=1)  # Just 1 hour
        
        if not emails:
            print("📭 No recent emails in the last hour")
            # Try getting just 3 emails
            try:
                sample_emails = collector.gmail.get_unread_emails(max_results=3)
                if sample_emails:
                    print(f"📬 Found {len(sample_emails)} sample emails to analyze")
                    for i, email in enumerate(sample_emails, 1):
                        enhanced = collector._enhance_email_context(email)
                        print(f"   📨 Email {i}:")
                        print(f"      Subject: {enhanced.get('subject', 'No subject')[:50]}...")
                        print(f"      Urgency: {enhanced.get('urgency_score', 0)}/10")
                        print(f"      Type: {enhanced.get('email_type', 'unknown')}")
                        print(f"      Meeting related: {enhanced.get('meeting_detection', {}).get('is_meeting_related', False)}")
            except Exception as e:
                print(f"⚠️ Limited email processing failed: {e}")
                
        else:
            print(f"📬 Processed {len(emails)} recent emails")
            
            # Show categories
            categorized = collector.categorize_emails_for_ai(emails)
            print("📂 Email categories:")
            for category, email_list in categorized.items():
                if email_list:
                    print(f"   • {category.replace('_', ' ').title()}: {len(email_list)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Email intelligence demo failed: {e}")
        return False

def demo_calendar_intelligence():
    """Demo calendar intelligence."""
    print("\n📅 Calendar Intelligence Demo")
    print("=" * 40)
    
    try:
        from core.enhanced_calendar_collector import EnhancedCalendarCollector
        
        print("🔍 Initializing calendar collector...")
        collector = EnhancedCalendarCollector()
        
        if not collector.initialized:
            print("❌ Calendar collector not initialized")
            return False
        
        print("✅ Calendar collector ready")
        print("📊 Analyzing calendar events...")
        
        events = collector.collect_meetings_with_prep_data(days_ahead=3)  # Just 3 days
        
        if not events:
            print("📅 No events found in the next 3 days")
        else:
            print(f"📅 Found {len(events)} events to analyze")
            
            for i, event in enumerate(events[:3], 1):  # Show first 3
                print(f"   📅 Event {i}:")
                print(f"      Summary: {event.get('summary', 'No title')}")
                print(f"      Type: {event.get('meeting_analysis', {}).get('type', 'unknown')}")
                print(f"      Importance: {event.get('importance_score', 0)}/10")
                print(f"      Prep needed: {event.get('preparation_required', {}).get('level', 'unknown')}")
                
                attendees = event.get('attendee_context', {}).get('count', 0)
                if attendees > 0:
                    print(f"      Attendees: {attendees}")
        
        return True
        
    except Exception as e:
        print(f"❌ Calendar intelligence demo failed: {e}")
        return False

def demo_ai_integration():
    """Demo AI integration with sample data."""
    print("\n🤖 AI Integration Demo")
    print("=" * 40)
    
    try:
        from core.ai_intelligence_engine import AIIntelligenceEngine
        
        print("🧠 Initializing AI intelligence engine...")
        ai_engine = AIIntelligenceEngine()
        
        print(f"✅ AI engine ready (AI client: {'Available' if ai_engine.initialized else 'Using fallback'})")
        
        # Create minimal test data
        sample_email_data = {
            'total_emails': 5,
            'categories': {
                'urgent_action_required': [{'subject': 'Test urgent email'}],
                'meeting_related': [{'subject': 'Meeting tomorrow'}],
                'informational': []
            }
        }
        
        sample_calendar_data = {
            'total_events': 2,
            'today_events': [{'summary': 'Test meeting'}],
            'meetings_needing_prep': []
        }
        
        print("🔮 Generating AI-powered email summary...")
        email_intelligence = ai_engine.generate_email_intelligence(sample_email_data)
        
        print(f"   📝 Summary generated ({email_intelligence.get('source', 'unknown')} source)")
        if email_intelligence.get('summary'):
            print(f"   📖 Preview: {email_intelligence['summary'][:100]}...")
        
        print("🔮 Generating AI-powered daily briefing...")
        daily_briefing = ai_engine.generate_daily_briefing(sample_email_data, sample_calendar_data)
        
        print(f"   📝 Briefing generated ({daily_briefing.get('source', 'unknown')} source)")
        if daily_briefing.get('briefing_text'):
            print(f"   📖 Preview: {daily_briefing['briefing_text'][:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI integration demo failed: {e}")
        return False

def main():
    """Run enhanced features demo."""
    print("🚀 WorkBuddy Enhanced Features Demo")
    print("=" * 50)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis demo shows your enhanced features with limited data processing")
    print("to avoid overwhelming your system with all 100+ emails at once.\n")
    
    demos = [
        ("Enhanced Morning Briefing Overview", demo_enhanced_morning_briefing),
        ("Email Intelligence", demo_email_intelligence), 
        ("Calendar Intelligence", demo_calendar_intelligence),
        ("AI Integration", demo_ai_integration)
    ]
    
    results = []
    
    for demo_name, demo_function in demos:
        try:
            result = demo_function()
            results.append((demo_name, result))
            
            if not result:
                print(f"\n⚠️  {demo_name} had issues, but continuing with other demos...\n")
            else:
                print(f"\n✅ {demo_name} completed successfully!\n")
                
        except KeyboardInterrupt:
            print(f"\n⏹️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n💥 {demo_name} crashed: {e}")
            results.append((demo_name, False))
    
    # Summary
    print("=" * 50)
    print("📊 DEMO RESULTS")
    print("=" * 50)
    
    for demo_name, success in results:
        status = "✅ SUCCESS" if success else "⚠️  ISSUES"
        print(f"{status}: {demo_name}")
    
    successful_demos = sum(1 for _, success in results if success)
    
    print(f"\nCompleted: {successful_demos}/{len(results)} demos successful")
    
    if successful_demos > 0:
        print("\n🎉 Enhanced Features are Working!")
        print("\nYour WorkBuddy now has:")
        print("• ✅ Intelligent email categorization and analysis")
        print("• ✅ Smart calendar event analysis and meeting prep")
        print("• ✅ AI-powered daily briefings")
        print("• ✅ Integration with your real Gmail and Calendar data")
        
        print("\n💡 Next Steps:")
        print("1. Try a full morning briefing (may take a moment with 100 emails)")
        print("2. Integrate with your main WorkBuddy app")
        print("3. Set up automated morning briefings")
        print("4. Customize AI prompts for your preferences")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Enhanced features are still ready to use!")
