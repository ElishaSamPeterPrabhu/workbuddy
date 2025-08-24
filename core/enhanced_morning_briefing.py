"""
Enhanced Morning Briefing System for WorkBuddy.
Integrates email intelligence, calendar analysis, and AI-powered insights.
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from core.morning_briefing import MorningBriefing
from core.enhanced_email_collector import EnhancedEmailCollector
from core.enhanced_calendar_collector import EnhancedCalendarCollector
from core.ai_intelligence_engine import AIIntelligenceEngine

logger = logging.getLogger(__name__)


class EnhancedMorningBriefing(MorningBriefing):
    """Enhanced morning briefing with AI-powered email and calendar intelligence."""
    
    def __init__(self):
        """Initialize enhanced morning briefing components."""
        super().__init__()
        
        # Initialize enhanced components
        self.email_collector = EnhancedEmailCollector()
        self.calendar_collector = EnhancedCalendarCollector()
        self.ai_engine = AIIntelligenceEngine()
        
        logger.info("Enhanced Morning Briefing initialized")
    
    def generate_enhanced_briefing(self) -> Dict[str, Any]:
        """Generate comprehensive AI-powered morning briefing."""
        try:
            logger.info("Starting enhanced morning briefing generation")
            
            # Collect raw data
            email_data = self.email_collector.get_email_summary_data()
            calendar_data = self.calendar_collector.get_calendar_summary_data()
            weather_data = self.get_weather()
            reminders = self._get_todays_reminders()
            
            # Generate AI intelligence
            briefing_components = {
                'greeting': self._generate_greeting(),
                'weather': self._format_weather_summary(weather_data),
                'email_intelligence': self.ai_engine.generate_email_intelligence(email_data),
                'calendar_intelligence': self.ai_engine.generate_calendar_intelligence(calendar_data),
                'reminders': self._format_reminders_summary(reminders),
                'daily_priorities': self._extract_daily_priorities(email_data, calendar_data)
            }
            
            # Generate comprehensive daily briefing
            daily_briefing = self.ai_engine.generate_daily_briefing(email_data, calendar_data)
            briefing_components['ai_briefing'] = daily_briefing
            
            # Format for delivery
            formatted_briefing = self._format_comprehensive_briefing(briefing_components)
            
            logger.info("Enhanced morning briefing generated successfully")
            return formatted_briefing
            
        except Exception as e:
            logger.error(f"Error generating enhanced briefing: {e}")
            # Fallback to basic briefing
            return self._generate_fallback_briefing()
    
    def _generate_greeting(self) -> str:
        """Generate personalized greeting based on time."""
        hour = datetime.now().hour
        day_name = datetime.now().strftime('%A')
        date_str = datetime.now().strftime('%B %d')
        
        if hour < 6:
            greeting = "Good early morning"
        elif hour < 12:
            greeting = "Good morning"
        elif hour < 17:
            greeting = "Good afternoon"
        else:
            greeting = "Good evening"
        
        return f"{greeting}! It's {day_name}, {date_str}."
    
    def _format_weather_summary(self, weather_data: Dict[str, Any]) -> str:
        """Format weather information for briefing."""
        if not weather_data:
            return "Weather information is unavailable."
        
        temperature = weather_data.get('temperature', 'Unknown')
        condition = weather_data.get('condition', 'Unknown')
        forecast = weather_data.get('forecast', '')
        
        summary = f"The weather is {condition} with a temperature of {temperature}."
        if forecast:
            summary += f" {forecast}"
        
        return summary
    
    def _format_reminders_summary(self, reminders: List[Dict[str, Any]]) -> str:
        """Format reminders for briefing."""
        if not reminders:
            return "You have no reminders set for today."
        
        if len(reminders) == 1:
            return f"You have 1 reminder: {reminders[0]['title']}"
        else:
            return f"You have {len(reminders)} reminders set for today."
    
    def _extract_daily_priorities(self, email_data: Dict[str, Any], calendar_data: Dict[str, Any]) -> List[str]:
        """Extract top daily priorities from email and calendar data."""
        priorities = []
        
        # High-priority emails
        urgent_emails = email_data.get('categories', {}).get('urgent_action_required', [])
        if urgent_emails:
            priorities.append(f"Address {len(urgent_emails)} urgent email(s)")
        
        # Important meetings
        high_importance_meetings = calendar_data.get('high_importance_meetings', [])
        for meeting in high_importance_meetings[:2]:  # Top 2
            priorities.append(f"Prepare for {meeting.get('summary', 'important meeting')}")
        
        # Task requests from emails
        task_emails = email_data.get('categories', {}).get('task_requests', [])
        if task_emails:
            priorities.append(f"Review {len(task_emails)} task request(s)")
        
        return priorities[:5]  # Top 5 priorities
    
    def _format_comprehensive_briefing(self, components: Dict[str, Any]) -> Dict[str, Any]:
        """Format all components into a comprehensive briefing."""
        
        # Create the main briefing text
        briefing_sections = []
        
        # Greeting and weather
        briefing_sections.append(components['greeting'])
        briefing_sections.append(components['weather'])
        
        # AI-generated daily briefing (main content)
        ai_briefing = components.get('ai_briefing', {})
        if ai_briefing.get('briefing_text'):
            briefing_sections.append(ai_briefing['briefing_text'])
        else:
            # Fallback to component summaries
            email_intel = components.get('email_intelligence', {})
            calendar_intel = components.get('calendar_intelligence', {})
            
            if email_intel.get('summary'):
                briefing_sections.append(f"Email Update: {email_intel['summary']}")
            
            if calendar_intel.get('summary'):
                briefing_sections.append(f"Calendar Overview: {calendar_intel['summary']}")
        
        # Reminders
        briefing_sections.append(components['reminders'])
        
        # Closing
        priorities = components.get('daily_priorities', [])
        if priorities:
            briefing_sections.append(f"Today's top priorities: {', '.join(priorities[:3])}")
        
        briefing_sections.append("How can I assist you today?")
        
        # Combine all sections
        full_briefing_text = " ".join(briefing_sections)
        
        return {
            'briefing_text': full_briefing_text,
            'components': components,
            'generated_at': datetime.now().isoformat(),
            'type': 'enhanced',
            'word_count': len(full_briefing_text.split()),
            'estimated_speak_time': len(full_briefing_text.split()) * 0.5  # ~2 words per second
        }
    
    def _generate_fallback_briefing(self) -> Dict[str, Any]:
        """Generate basic briefing if enhanced version fails."""
        try:
            # Use the original morning briefing as fallback
            basic_briefing_text = super().generate_morning_briefing()
            
            return {
                'briefing_text': basic_briefing_text,
                'components': {
                    'greeting': self._generate_greeting(),
                    'weather': self._format_weather_summary(self.get_weather()),
                    'fallback': True
                },
                'generated_at': datetime.now().isoformat(),
                'type': 'fallback',
                'word_count': len(basic_briefing_text.split()),
                'estimated_speak_time': len(basic_briefing_text.split()) * 0.5
            }
        except Exception as e:
            logger.error(f"Even fallback briefing failed: {e}")
            return {
                'briefing_text': "Good morning! I'm having trouble generating your briefing right now, but I'm here to help with whatever you need.",
                'components': {'error': True},
                'generated_at': datetime.now().isoformat(),
                'type': 'error',
                'word_count': 20,
                'estimated_speak_time': 10
            }
    
    def deliver_enhanced_briefing(self, callback=None) -> Dict[str, Any]:
        """Deliver the enhanced morning briefing with voice."""
        briefing_data = self.generate_enhanced_briefing()
        briefing_text = briefing_data['briefing_text']
        
        # Log the briefing
        logger.info(f"Enhanced morning briefing: {briefing_text[:100]}...")
        
        # Store last briefing time and data
        from core.storage import set_user_preference
        set_user_preference('last_briefing', datetime.now().isoformat())
        set_user_preference('last_briefing_type', briefing_data['type'])
        
        # Deliver via voice in a separate thread
        def speak_briefing():
            try:
                self.voice.speak(briefing_text)
                if callback:
                    callback(briefing_data)
            except Exception as e:
                logger.error(f"Error in voice delivery: {e}")
                if callback:
                    callback(briefing_data)
        
        import threading
        thread = threading.Thread(target=speak_briefing)
        thread.daemon = True
        thread.start()
        
        return briefing_data
    
    def get_meeting_preparation_briefing(self, event_id: Optional[str] = None) -> Dict[str, Any]:
        """Get preparation briefing for a specific meeting or next meeting."""
        try:
            # Get calendar data
            calendar_data = self.calendar_collector.get_calendar_summary_data(days_ahead=1)
            meetings_needing_prep = calendar_data.get('meetings_needing_prep', [])
            
            if not meetings_needing_prep:
                return {
                    'message': 'No meetings requiring preparation found.',
                    'type': 'no_prep_needed'
                }
            
            # Get the next meeting needing preparation
            target_meeting = meetings_needing_prep[0]  # Most urgent first
            
            # Generate AI-powered preparation briefing
            prep_briefing = self.ai_engine.generate_meeting_preparation(target_meeting)
            
            return {
                'meeting_summary': target_meeting.get('summary', ''),
                'preparation_briefing': prep_briefing,
                'estimated_prep_time': target_meeting.get('preparation_required', {}).get('estimated_minutes', 10),
                'type': 'meeting_preparation'
            }
            
        except Exception as e:
            logger.error(f"Error generating meeting preparation: {e}")
            return {
                'message': 'Unable to generate meeting preparation at this time.',
                'type': 'error'
            }
    
    def get_email_priority_briefing(self) -> Dict[str, Any]:
        """Get briefing focused on email priorities."""
        try:
            email_data = self.email_collector.get_email_summary_data()
            email_intelligence = self.ai_engine.generate_email_intelligence(email_data)
            
            categories = email_data.get('categories', {})
            urgent_count = len(categories.get('urgent_action_required', []))
            total_count = email_data.get('total_emails', 0)
            
            if total_count == 0:
                return {
                    'message': 'Your inbox is all caught up!',
                    'type': 'no_emails'
                }
            
            priority_briefing = f"""
            Email Priority Update: You have {total_count} emails, with {urgent_count} requiring urgent attention.
            
            {email_intelligence.get('summary', 'No detailed analysis available.')}
            """
            
            return {
                'briefing_text': priority_briefing.strip(),
                'urgent_count': urgent_count,
                'total_count': total_count,
                'intelligence': email_intelligence,
                'type': 'email_priorities'
            }
            
        except Exception as e:
            logger.error(f"Error generating email briefing: {e}")
            return {
                'message': 'Unable to generate email briefing at this time.',
                'type': 'error'
            }
    
    def should_deliver_enhanced_briefing(self) -> bool:
        """Check if we should deliver the enhanced morning briefing."""
        # Use the same logic as the base class
        return super().should_deliver_briefing()
    
    def get_briefing_summary(self) -> Dict[str, Any]:
        """Get a summary of what would be included in the briefing without generating it."""
        try:
            # Quick data collection for preview
            email_data = self.email_collector.get_email_summary_data()
            calendar_data = self.calendar_collector.get_calendar_summary_data()
            
            categories = email_data.get('categories', {})
            
            return {
                'email_counts': {k: len(v) for k, v in categories.items()},
                'calendar_counts': {
                    'today_events': len(calendar_data.get('today_events', [])),
                    'prep_needed': len(calendar_data.get('meetings_needing_prep', [])),
                    'high_importance': len(calendar_data.get('high_importance_meetings', []))
                },
                'weather_available': bool(self.get_weather()),
                'reminders_count': len(self._get_todays_reminders()),
                'estimated_briefing_time': 120  # seconds
            }
            
        except Exception as e:
            logger.error(f"Error generating briefing summary: {e}")
            return {'error': str(e)}
