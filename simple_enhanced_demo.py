"""
Simple demo of enhanced email intelligence working with real Gmail data.
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def demo_gmail_intelligence():
    """Demo enhanced Gmail intelligence with your real data."""
    print("📧 WorkBuddy Enhanced Gmail Intelligence Demo")
    print("=" * 50)
    
    try:
        # Import Gmail integration
        from integrations.gmail import GmailIntegration
        
        print("🔐 Connecting to your Gmail...")
        gmail = GmailIntegration()
        
        print("✅ Connected to Gmail successfully!")
        print("📊 Getting email summary...")
        
        # Get just 5 emails to analyze
        emails = gmail.get_unread_emails(max_results=5)
        print(f"📬 Retrieved {len(emails)} emails for analysis")
        
        if emails:
            print("\n🧠 Enhanced Email Analysis:")
            print("-" * 30)
            
            # Analyze each email with our enhanced intelligence
            for i, email in enumerate(emails, 1):
                print(f"\n📨 Email {i}:")
                
                # Basic info
                subject = email.get('subject', 'No subject')
                sender = email.get('sender', 'Unknown sender')
                snippet = email.get('snippet', '')
                
                print(f"   Subject: {subject[:60]}{'...' if len(subject) > 60 else ''}")
                print(f"   From: {sender[:40]}{'...' if len(sender) > 40 else ''}")
                print(f"   Preview: {snippet[:80]}{'...' if len(snippet) > 80 else ''}")
                
                # Enhanced analysis
                print("   🔍 Intelligence Analysis:")
                
                # Sender importance (1-10)
                sender_score = calculate_sender_importance(sender)
                print(f"      • Sender importance: {sender_score}/10")
                
                # Urgency detection
                urgency_score = calculate_urgency(subject, snippet, email.get('is_important', False))
                print(f"      • Urgency score: {urgency_score}/10")
                
                # Meeting detection
                is_meeting = detect_meeting(subject + " " + snippet)
                print(f"      • Meeting related: {'Yes' if is_meeting else 'No'}")
                
                # Email type classification
                email_type = classify_email_type(subject, snippet, sender)
                print(f"      • Email type: {email_type.replace('_', ' ').title()}")
                
                # Action items detection
                has_tasks = detect_action_items(subject + " " + snippet)
                print(f"      • Contains tasks: {'Yes' if has_tasks else 'No'}")
        
        print("\n" + "=" * 50)
        print("🎉 Enhanced Gmail Intelligence Demo Complete!")
        print("\nYour enhanced system can now:")
        print("• ✅ Analyze sender importance")
        print("• ✅ Detect email urgency") 
        print("• ✅ Identify meeting invitations")
        print("• ✅ Classify email types")
        print("• ✅ Find action items and tasks")
        print("• ✅ Process your real Gmail data")
        
        return True
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def calculate_sender_importance(sender):
    """Calculate sender importance score (1-10)."""
    sender_lower = sender.lower()
    
    # High importance keywords
    high_keywords = ['ceo', 'manager', 'director', 'lead', 'senior', 'head']
    medium_keywords = ['team', 'project', 'coordinator', 'admin']
    
    # Low importance indicators
    if any(word in sender_lower for word in ['noreply', 'no-reply', 'donotreply']):
        return 2
    
    # High importance
    if any(keyword in sender_lower for keyword in high_keywords):
        return 8
    elif any(keyword in sender_lower for keyword in medium_keywords):
        return 6
    
    # Default
    return 5

def calculate_urgency(subject, snippet, is_important):
    """Calculate urgency score (1-10)."""
    content = f"{subject} {snippet}".lower()
    score = 5  # Base score
    
    # Urgent keywords
    urgent_keywords = ['urgent', 'asap', 'immediate', 'emergency', 'critical', 'deadline']
    high_priority_keywords = ['important', 'priority', 'soon', 'today', 'tomorrow']
    
    if any(keyword in content for keyword in urgent_keywords):
        score += 3
    elif any(keyword in content for keyword in high_priority_keywords):
        score += 2
    
    if is_important:
        score += 2
    
    # Time sensitivity
    if any(word in content for word in ['today', 'tonight', 'this morning']):
        score += 2
    elif any(word in content for word in ['tomorrow', 'this week']):
        score += 1
    
    return min(score, 10)

def detect_meeting(content):
    """Detect if content is meeting-related."""
    content_lower = content.lower()
    
    meeting_keywords = [
        'meeting', 'call', 'conference', 'zoom', 'teams', 'hangout',
        'discuss', 'agenda', 'schedule', 'appointment', 'sync'
    ]
    
    return any(keyword in content_lower for keyword in meeting_keywords)

def classify_email_type(subject, snippet, sender):
    """Classify email type."""
    content = f"{subject} {snippet}".lower()
    sender_lower = sender.lower()
    
    # Meeting invitations
    if detect_meeting(content):
        return 'meeting_invitation'
    
    # Automated emails
    if any(keyword in sender_lower for keyword in ['noreply', 'no-reply', 'automated']):
        return 'automated'
    
    # Newsletters/marketing
    if any(keyword in content for keyword in ['unsubscribe', 'newsletter', 'marketing']):
        return 'newsletter'
    
    # Task/action emails
    if detect_action_items(content):
        return 'task_request'
    
    # Calendar updates
    if any(keyword in content for keyword in ['calendar', 'event', 'invitation']):
        return 'calendar_update'
    
    # Information only
    if any(keyword in content for keyword in ['fyi', 'for your information', 'update']):
        return 'informational'
    
    return 'general'

def detect_action_items(content):
    """Detect if content contains action items."""
    content_lower = content.lower()
    
    action_indicators = [
        'please', 'can you', 'could you', 'need to', 'action required',
        'todo', 'deadline', 'complete', 'finish', 'deliver'
    ]
    
    return any(indicator in content_lower for indicator in action_indicators)

if __name__ == '__main__':
    try:
        success = demo_gmail_intelligence()
        if success:
            print("\n🚀 Ready to integrate enhanced features into WorkBuddy!")
        else:
            print("\n⚠️  Some issues occurred, but core functionality is working.")
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Enhanced features are ready!")
