"""
AI Intelligence Engine for WorkBuddy.
Processes email and calendar data to generate intelligent summaries and insights.
"""

import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from core.ai_client import AIClient

logger = logging.getLogger(__name__)


class AIIntelligenceEngine:
    """AI-powered intelligence engine for processing and summarizing data."""
    
    def __init__(self, ai_client: Optional[AIClient] = None):
        """Initialize the AI intelligence engine."""
        try:
            self.ai_client = ai_client or AIClient()
            self.initialized = True
            logger.info("AI Intelligence Engine initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI client: {e}")
            self.ai_client = None
            self.initialized = False
    
    def generate_email_intelligence(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered email intelligence and summaries.
        
        Args:
            email_data: Enhanced email data from EnhancedEmailCollector
            
        Returns:
            AI-generated email insights and summaries
        """
        if not self.initialized:
            return self._fallback_email_summary(email_data)
        
        try:
            prompt = self._create_email_summary_prompt(email_data)
            
            ai_response = self.ai_client.get_response(prompt)
            
            # Parse AI response (assuming it returns structured data)
            if ai_response:
                return self._parse_email_intelligence(ai_response, email_data)
            else:
                return self._fallback_email_summary(email_data)
                
        except Exception as e:
            logger.error(f"Error generating email intelligence: {e}")
            return self._fallback_email_summary(email_data)
    
    def generate_calendar_intelligence(self, calendar_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered calendar intelligence and meeting preparation.
        
        Args:
            calendar_data: Enhanced calendar data from EnhancedCalendarCollector
            
        Returns:
            AI-generated calendar insights and meeting preparations
        """
        if not self.initialized:
            return self._fallback_calendar_summary(calendar_data)
        
        try:
            prompt = self._create_calendar_summary_prompt(calendar_data)
            
            ai_response = self.ai_client.get_response(prompt)
            
            if ai_response:
                return self._parse_calendar_intelligence(ai_response, calendar_data)
            else:
                return self._fallback_calendar_summary(calendar_data)
                
        except Exception as e:
            logger.error(f"Error generating calendar intelligence: {e}")
            return self._fallback_calendar_summary(calendar_data)
    
    def generate_meeting_preparation(self, meeting_event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered meeting preparation briefing.
        
        Args:
            meeting_event: Single meeting event with enhanced context
            
        Returns:
            AI-generated meeting preparation briefing
        """
        if not self.initialized:
            return self._fallback_meeting_prep(meeting_event)
        
        try:
            prompt = self._create_meeting_prep_prompt(meeting_event)
            
            ai_response = self.ai_client.get_response(prompt)
            
            if ai_response:
                return self._parse_meeting_preparation(ai_response, meeting_event)
            else:
                return self._fallback_meeting_prep(meeting_event)
                
        except Exception as e:
            logger.error(f"Error generating meeting preparation: {e}")
            return self._fallback_meeting_prep(meeting_event)
    
    def generate_daily_briefing(self, email_data: Dict[str, Any], calendar_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive daily briefing combining email and calendar intelligence.
        
        Args:
            email_data: Enhanced email summary data
            calendar_data: Enhanced calendar summary data
            
        Returns:
            Complete AI-generated daily briefing
        """
        if not self.initialized:
            return self._fallback_daily_briefing(email_data, calendar_data)
        
        try:
            # Get individual intelligences
            email_intelligence = self.generate_email_intelligence(email_data)
            calendar_intelligence = self.generate_calendar_intelligence(calendar_data)
            
            # Create comprehensive briefing prompt
            prompt = self._create_daily_briefing_prompt(email_intelligence, calendar_intelligence)
            
            ai_response = self.ai_client.get_response(prompt)
            
            if ai_response:
                return self._parse_daily_briefing(ai_response, email_intelligence, calendar_intelligence)
            else:
                return self._fallback_daily_briefing(email_data, calendar_data)
                
        except Exception as e:
            logger.error(f"Error generating daily briefing: {e}")
            return self._fallback_daily_briefing(email_data, calendar_data)
    
    # Prompt Creation Methods
    
    def _create_email_summary_prompt(self, email_data: Dict[str, Any]) -> str:
        """Create AI prompt for email summarization."""
        categories = email_data.get('categories', {})
        total_emails = email_data.get('total_emails', 0)
        
        prompt = f"""
You are an intelligent assistant analyzing {total_emails} emails. Provide a concise, actionable summary.

EMAIL BREAKDOWN:
- Urgent Action Required: {len(categories.get('urgent_action_required', []))} emails
- Meeting Related: {len(categories.get('meeting_related', []))} emails
- Task Requests: {len(categories.get('task_requests', []))} emails
- Informational: {len(categories.get('informational', []))} emails
- Calendar Updates: {len(categories.get('calendar_updates', []))} emails
- Automated: {len(categories.get('automated', []))} emails

Focus on:
1. Most urgent items requiring immediate attention
2. Important meetings or calendar changes
3. Key tasks with deadlines
4. Notable communications from important senders

For each priority item, provide:
- Brief summary
- Required action (if any)
- Urgency level
- Recommended timing

Keep response concise but informative. Prioritize actionable insights.

Raw email data summary: {json.dumps({k: len(v) for k, v in categories.items()}, indent=2)}
"""
        return prompt
    
    def _create_calendar_summary_prompt(self, calendar_data: Dict[str, Any]) -> str:
        """Create AI prompt for calendar summarization."""
        today_events = calendar_data.get('today_events', [])
        upcoming_events = calendar_data.get('upcoming_events', [])
        prep_needed = calendar_data.get('meetings_needing_prep', [])
        
        prompt = f"""
You are an intelligent assistant analyzing calendar events. Provide a helpful daily schedule overview.

CALENDAR OVERVIEW:
- Today's Events: {len(today_events)}
- Upcoming Events: {len(upcoming_events)}
- Meetings Needing Preparation: {len(prep_needed)}

Focus on:
1. Today's schedule and timing
2. Meetings requiring preparation
3. Important or high-priority meetings
4. Scheduling conflicts or tight timing
5. Meeting preparation recommendations

For today's events, provide:
- Time and brief description
- Preparation needed (if any)
- Key attendees or importance level

For upcoming important events, mention:
- When they are
- Why they're important
- Advance preparation needed

Keep response practical and focused on helping plan the day effectively.
"""
        return prompt
    
    def _create_meeting_prep_prompt(self, meeting_event: Dict[str, Any]) -> str:
        """Create AI prompt for meeting preparation."""
        summary = meeting_event.get('summary', 'Meeting')
        description = meeting_event.get('description', '')
        attendees = meeting_event.get('attendee_context', {})
        prep_requirements = meeting_event.get('preparation_required', {})
        
        prompt = f"""
You are an intelligent assistant helping prepare for a meeting: "{summary}"

MEETING DETAILS:
- Type: {meeting_event.get('meeting_analysis', {}).get('type', 'general')}
- Attendees: {attendees.get('count', 0)} people
- Has External Attendees: {attendees.get('has_external', False)}
- VIP Attendees: {', '.join(attendees.get('vip_attendees', []))}
- Preparation Level: {prep_requirements.get('level', 'medium')}
- Estimated Prep Time: {prep_requirements.get('estimated_minutes', 10)} minutes

DESCRIPTION: {description[:500] if description else 'No description provided'}

Provide a concise meeting preparation briefing including:
1. Key objectives and agenda (inferred from available info)
2. Important attendees and their likely interests/concerns
3. Preparation recommendations and materials needed
4. Key talking points or questions to consider
5. Potential discussion topics or decisions needed

Keep response focused and actionable. Tailor advice to meeting type and attendee composition.
"""
        return prompt
    
    def _create_daily_briefing_prompt(self, email_intelligence: Dict[str, Any], calendar_intelligence: Dict[str, Any]) -> str:
        """Create AI prompt for comprehensive daily briefing."""
        prompt = f"""
You are an intelligent personal assistant providing a daily briefing. Create a cohesive, helpful overview.

EMAIL INTELLIGENCE:
{email_intelligence.get('summary', 'No email summary available')}

CALENDAR INTELLIGENCE:
{calendar_intelligence.get('summary', 'No calendar summary available')}

Create a comprehensive daily briefing that:
1. Highlights the most important items across both email and calendar
2. Identifies connections between emails and meetings
3. Suggests an optimal order for tackling priorities
4. Provides time management recommendations
5. Alerts to any scheduling conflicts or urgent deadlines

Format as a natural, conversational briefing that would be helpful when spoken aloud.
Keep it concise but complete - aim for 2-3 minutes when spoken.
Focus on actionable insights and clear next steps.
"""
        return prompt
    
    # Response Parsing Methods
    
    def _parse_email_intelligence(self, ai_response: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI email intelligence response."""
        return {
            'summary': ai_response,
            'total_emails': original_data.get('total_emails', 0),
            'priority_items': self._extract_priority_items(ai_response),
            'action_required': self._extract_actions(ai_response),
            'generated_at': datetime.now().isoformat(),
            'source': 'ai_generated'
        }
    
    def _parse_calendar_intelligence(self, ai_response: str, original_data: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI calendar intelligence response."""
        return {
            'summary': ai_response,
            'total_events': original_data.get('total_events', 0),
            'today_focus': self._extract_today_focus(ai_response),
            'preparation_alerts': self._extract_prep_alerts(ai_response),
            'generated_at': datetime.now().isoformat(),
            'source': 'ai_generated'
        }
    
    def _parse_meeting_preparation(self, ai_response: str, original_event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI meeting preparation response."""
        return {
            'briefing': ai_response,
            'meeting_summary': original_event.get('summary', ''),
            'key_points': self._extract_key_points(ai_response),
            'action_items': self._extract_prep_actions(ai_response),
            'generated_at': datetime.now().isoformat(),
            'source': 'ai_generated'
        }
    
    def _parse_daily_briefing(self, ai_response: str, email_intel: Dict[str, Any], calendar_intel: Dict[str, Any]) -> Dict[str, Any]:
        """Parse AI daily briefing response."""
        return {
            'briefing_text': ai_response,
            'email_summary': email_intel.get('summary', ''),
            'calendar_summary': calendar_intel.get('summary', ''),
            'key_priorities': self._extract_priorities(ai_response),
            'time_recommendations': self._extract_time_advice(ai_response),
            'generated_at': datetime.now().isoformat(),
            'source': 'ai_generated'
        }
    
    # Fallback Methods (when AI is not available)
    
    def _fallback_email_summary(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic email summary without AI."""
        categories = email_data.get('categories', {})
        total_emails = email_data.get('total_emails', 0)
        
        summary_parts = [f"You have {total_emails} emails to review."]
        
        if categories.get('urgent_action_required'):
            summary_parts.append(f"{len(categories['urgent_action_required'])} require immediate attention.")
        
        if categories.get('meeting_related'):
            summary_parts.append(f"{len(categories['meeting_related'])} are meeting-related.")
        
        if categories.get('task_requests'):
            summary_parts.append(f"{len(categories['task_requests'])} contain task requests.")
        
        return {
            'summary': ' '.join(summary_parts),
            'total_emails': total_emails,
            'priority_items': categories.get('urgent_action_required', [])[:3],
            'action_required': len(categories.get('urgent_action_required', [])) > 0,
            'generated_at': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def _fallback_calendar_summary(self, calendar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic calendar summary without AI."""
        today_events = calendar_data.get('today_events', [])
        prep_needed = calendar_data.get('meetings_needing_prep', [])
        
        if not today_events:
            summary = "Your calendar is clear today."
        else:
            summary = f"You have {len(today_events)} events today."
            if prep_needed:
                summary += f" {len(prep_needed)} meetings may need preparation."
        
        return {
            'summary': summary,
            'total_events': len(today_events),
            'today_focus': [e.get('summary', '') for e in today_events[:3]],
            'preparation_alerts': len(prep_needed),
            'generated_at': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def _fallback_meeting_prep(self, meeting_event: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic meeting preparation without AI."""
        summary = meeting_event.get('summary', 'Meeting')
        attendees = meeting_event.get('attendee_context', {})
        prep_requirements = meeting_event.get('preparation_required', {})
        
        briefing_parts = [f"Upcoming meeting: {summary}"]
        
        if attendees.get('count', 0) > 1:
            briefing_parts.append(f"With {attendees['count']} attendees.")
        
        if prep_requirements.get('level') == 'high':
            briefing_parts.append("High preparation recommended.")
        
        checklist = prep_requirements.get('preparation_checklist', [])
        if checklist:
            briefing_parts.append(f"Consider: {', '.join(checklist[:3])}")
        
        return {
            'briefing': ' '.join(briefing_parts),
            'meeting_summary': summary,
            'key_points': checklist[:3],
            'action_items': checklist,
            'generated_at': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def _fallback_daily_briefing(self, email_data: Dict[str, Any], calendar_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic daily briefing without AI."""
        email_count = email_data.get('total_emails', 0)
        event_count = len(calendar_data.get('today_events', []))
        
        briefing_parts = []
        
        if email_count > 0:
            briefing_parts.append(f"You have {email_count} emails to review.")
        
        if event_count > 0:
            briefing_parts.append(f"You have {event_count} events scheduled today.")
        
        if not briefing_parts:
            briefing_parts.append("You have a light schedule today.")
        
        return {
            'briefing_text': ' '.join(briefing_parts),
            'email_summary': self._fallback_email_summary(email_data)['summary'],
            'calendar_summary': self._fallback_calendar_summary(calendar_data)['summary'],
            'key_priorities': [],
            'time_recommendations': [],
            'generated_at': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    # Utility Methods for Parsing AI Responses
    
    def _extract_priority_items(self, response: str) -> List[str]:
        """Extract priority items from AI response."""
        # Simple extraction - in production, use more sophisticated parsing
        lines = response.split('\n')
        priorities = []
        for line in lines:
            if any(word in line.lower() for word in ['urgent', 'priority', 'important', 'immediate']):
                priorities.append(line.strip())
        return priorities[:5]
    
    def _extract_actions(self, response: str) -> bool:
        """Check if response indicates actions are required."""
        action_indicators = ['action required', 'need to', 'should', 'must', 'deadline']
        return any(indicator in response.lower() for indicator in action_indicators)
    
    def _extract_today_focus(self, response: str) -> List[str]:
        """Extract today's focus items from calendar response."""
        lines = response.split('\n')
        focus_items = []
        for line in lines:
            if any(word in line.lower() for word in ['today', 'this morning', 'this afternoon']):
                focus_items.append(line.strip())
        return focus_items[:5]
    
    def _extract_prep_alerts(self, response: str) -> List[str]:
        """Extract preparation alerts from response."""
        lines = response.split('\n')
        alerts = []
        for line in lines:
            if any(word in line.lower() for word in ['prepare', 'preparation', 'ready', 'review']):
                alerts.append(line.strip())
        return alerts[:3]
    
    def _extract_key_points(self, response: str) -> List[str]:
        """Extract key points from meeting prep response."""
        lines = response.split('\n')
        key_points = []
        for line in lines:
            if line.strip().startswith(('1.', '2.', '3.', '-', '•')):
                key_points.append(line.strip())
        return key_points[:5]
    
    def _extract_prep_actions(self, response: str) -> List[str]:
        """Extract preparation actions from meeting prep response."""
        return self._extract_key_points(response)  # Same logic for now
    
    def _extract_priorities(self, response: str) -> List[str]:
        """Extract priorities from daily briefing."""
        return self._extract_priority_items(response)
    
    def _extract_time_advice(self, response: str) -> List[str]:
        """Extract time management advice from daily briefing."""
        lines = response.split('\n')
        advice = []
        for line in lines:
            if any(word in line.lower() for word in ['time', 'schedule', 'plan', 'order', 'first', 'then']):
                advice.append(line.strip())
        return advice[:3]
