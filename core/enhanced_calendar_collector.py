"""
Enhanced Calendar Data Collector for WorkBuddy.
Collects and analyzes calendar events for AI processing and meeting preparation.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from integrations.calendar import GoogleCalendarIntegration
import re

logger = logging.getLogger(__name__)


class EnhancedCalendarCollector:
    """Enhanced calendar collection and analysis for AI processing."""
    
    def __init__(self):
        """Initialize the enhanced calendar collector."""
        try:
            self.calendar = GoogleCalendarIntegration()
            self.initialized = self.calendar.authenticate()
            if self.initialized:
                logger.info("Enhanced calendar collector initialized successfully")
            else:
                logger.warning("Calendar authentication failed")
        except Exception as e:
            logger.error(f"Failed to initialize Calendar integration: {e}")
            self.calendar = None
            self.initialized = False
    
    def collect_meetings_with_prep_data(self, days_ahead: int = 7) -> List[Dict[str, Any]]:
        """
        Collect calendar events with preparation context.
        
        Args:
            days_ahead: Number of days ahead to look for events
            
        Returns:
            List of events with enhanced preparation data
        """
        if not self.initialized:
            logger.warning("Calendar collector not initialized")
            return []
        
        try:
            # Get upcoming events
            events = self.calendar.get_events(
                start=datetime.now(),
                end=datetime.now() + timedelta(days=days_ahead)
            )
            
            enhanced_events = []
            for event in events:
                enhanced_event = self._enhance_event_context(event)
                enhanced_events.append(enhanced_event)
            
            logger.info(f"Collected {len(enhanced_events)} events with enhanced context")
            return enhanced_events
            
        except Exception as e:
            logger.error(f"Error collecting calendar events: {e}")
            return []
    
    def _enhance_event_context(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add preparation context and intelligence to event data."""
        enhanced = event.copy()
        
        # Extract event details
        summary = event.get('summary', '')
        description = event.get('description', '')
        
        # Analyze meeting type and requirements
        enhanced['meeting_analysis'] = self._analyze_meeting_type(summary, description)
        
        # Extract attendee information
        enhanced['attendee_context'] = self._analyze_attendees(event.get('attendees', []))
        
        # Assess preparation requirements
        enhanced['preparation_required'] = self._assess_prep_requirements(event)
        
        # Extract agenda items
        enhanced['agenda_items'] = self._extract_agenda_items(description)
        
        # Calculate meeting importance
        enhanced['importance_score'] = self._calculate_meeting_importance(event)
        
        # Determine if reminder is needed
        enhanced['reminder_needed'] = self._needs_preparation_reminder(event)
        
        return enhanced
    
    def _analyze_meeting_type(self, summary: str, description: str) -> Dict[str, Any]:
        """Analyze the type and nature of the meeting."""
        content = f"{summary} {description}".lower()
        
        meeting_types = {
            'standup': ['standup', 'daily standup', 'scrum', 'daily scrum'],
            'one_on_one': ['1:1', 'one on one', '1-on-1', 'one-on-one', 'check-in'],
            'review': ['review', 'retrospective', 'retro', 'post-mortem'],
            'planning': ['planning', 'sprint planning', 'roadmap', 'strategy'],
            'presentation': ['presentation', 'demo', 'showcase', 'pitch'],
            'interview': ['interview', 'screening', 'candidate'],
            'training': ['training', 'workshop', 'learning', 'onboarding'],
            'client_meeting': ['client', 'customer', 'external'],
            'team_meeting': ['team meeting', 'team sync', 'all hands'],
            'general': []
        }
        
        detected_type = 'general'
        for meeting_type, keywords in meeting_types.items():
            if any(keyword in content for keyword in keywords):
                detected_type = meeting_type
                break
        
        # Analyze meeting characteristics
        is_recurring = self._detect_recurring_pattern(content)
        estimated_prep_time = self._estimate_prep_time(detected_type, content)
        
        return {
            'type': detected_type,
            'is_recurring': is_recurring,
            'estimated_prep_time_minutes': estimated_prep_time,
            'requires_materials': self._requires_materials(detected_type, content)
        }
    
    def _analyze_attendees(self, attendees: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze attendee information for context."""
        if not attendees:
            return {
                'count': 0,
                'has_external': False,
                'vip_attendees': [],
                'size_category': 'solo'
            }
        
        attendee_count = len(attendees)
        external_domains = []
        vip_indicators = ['ceo', 'director', 'manager', 'lead', 'head', 'vp', 'president']
        
        vip_attendees = []
        for attendee in attendees:
            email = attendee.get('email', '')
            display_name = attendee.get('displayName', email)
            
            # Check for external attendees (different domain)
            if '@' in email and not any(domain in email for domain in ['gmail.com', 'company.com']):
                external_domains.append(email.split('@')[1])
            
            # Check for VIP attendees
            if any(indicator in display_name.lower() for indicator in vip_indicators):
                vip_attendees.append(display_name)
        
        # Categorize meeting size
        if attendee_count <= 2:
            size_category = 'small'
        elif attendee_count <= 5:
            size_category = 'medium'
        else:
            size_category = 'large'
        
        return {
            'count': attendee_count,
            'has_external': len(external_domains) > 0,
            'external_domains': list(set(external_domains)),
            'vip_attendees': vip_attendees,
            'size_category': size_category
        }
    
    def _assess_prep_requirements(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Assess what preparation is needed for this meeting."""
        summary = event.get('summary', '').lower()
        description = event.get('description', '').lower()
        content = f"{summary} {description}"
        
        # High-prep indicators
        high_prep_keywords = [
            'presentation', 'demo', 'pitch', 'proposal', 'review', 'interview',
            'quarterly', 'board', 'executive', 'client', 'customer'
        ]
        
        # Medium-prep indicators
        medium_prep_keywords = [
            'planning', 'strategy', 'retrospective', 'one-on-one', 'performance'
        ]
        
        # Low-prep indicators
        low_prep_keywords = [
            'standup', 'daily', 'check-in', 'casual', 'coffee'
        ]
        
        # Determine prep level
        if any(keyword in content for keyword in high_prep_keywords):
            prep_level = 'high'
            prep_time = 30
        elif any(keyword in content for keyword in medium_prep_keywords):
            prep_level = 'medium'
            prep_time = 15
        elif any(keyword in content for keyword in low_prep_keywords):
            prep_level = 'low'
            prep_time = 5
        else:
            prep_level = 'medium'
            prep_time = 10
        
        # Check for specific preparation needs
        needs_documents = any(word in content for word in [
            'document', 'report', 'presentation', 'slides', 'materials'
        ])
        
        needs_data = any(word in content for word in [
            'data', 'metrics', 'numbers', 'statistics', 'analytics'
        ])
        
        needs_agenda = any(word in content for word in [
            'agenda', 'topics', 'items', 'discuss'
        ])
        
        return {
            'level': prep_level,
            'estimated_minutes': prep_time,
            'needs_documents': needs_documents,
            'needs_data': needs_data,
            'needs_agenda': needs_agenda,
            'preparation_checklist': self._create_prep_checklist(prep_level, content)
        }
    
    def _extract_agenda_items(self, description: str) -> List[str]:
        """Extract agenda items from meeting description."""
        if not description:
            return []
        
        agenda_items = []
        
        # Look for numbered lists
        numbered_pattern = r'^\s*\d+\.?\s*(.+)$'
        for line in description.split('\n'):
            match = re.match(numbered_pattern, line.strip())
            if match:
                agenda_items.append(match.group(1).strip())
        
        # Look for bullet points
        bullet_pattern = r'^\s*[-*•]\s*(.+)$'
        for line in description.split('\n'):
            match = re.match(bullet_pattern, line.strip())
            if match:
                agenda_items.append(match.group(1).strip())
        
        # Look for "discuss" or "review" items
        discuss_pattern = r'(discuss|review|talk about|cover)\s+(.{10,50})'
        for match in re.finditer(discuss_pattern, description.lower()):
            agenda_items.append(match.group(2).strip())
        
        return agenda_items[:5]  # Limit to 5 items
    
    def _calculate_meeting_importance(self, event: Dict[str, Any]) -> int:
        """Calculate meeting importance score (1-10)."""
        score = 5  # Base score
        
        summary = event.get('summary', '').lower()
        description = event.get('description', '').lower()
        attendees = event.get('attendees', [])
        
        # High importance keywords
        high_importance = ['board', 'executive', 'ceo', 'quarterly', 'annual', 'client']
        if any(keyword in f"{summary} {description}" for keyword in high_importance):
            score += 3
        
        # Large meetings are typically important
        if len(attendees) > 5:
            score += 2
        
        # External attendees increase importance
        attendee_context = self._analyze_attendees(attendees)
        if attendee_context['has_external']:
            score += 2
        
        # VIP attendees increase importance
        if attendee_context['vip_attendees']:
            score += 2
        
        # Long meetings might be more important
        duration = self._calculate_duration(event)
        if duration > 60:  # More than 1 hour
            score += 1
        
        return min(score, 10)
    
    def _needs_preparation_reminder(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Determine if and when to send preparation reminders."""
        prep_requirements = event.get('preparation_required', {})
        importance = event.get('importance_score', 5)
        prep_level = prep_requirements.get('level', 'medium')
        
        # Calculate reminder timing based on preparation needs
        if prep_level == 'high' or importance >= 8:
            reminder_minutes = [60, 15]  # 1 hour and 15 minutes before
        elif prep_level == 'medium' or importance >= 6:
            reminder_minutes = [30]  # 30 minutes before
        else:
            reminder_minutes = [10]  # 10 minutes before
        
        return {
            'needs_reminder': prep_level != 'low' or importance >= 6,
            'reminder_times': reminder_minutes,
            'reminder_message': self._create_reminder_message(event)
        }
    
    def _detect_recurring_pattern(self, content: str) -> bool:
        """Detect if this is a recurring meeting."""
        recurring_indicators = [
            'daily', 'weekly', 'monthly', 'standup', 'scrum', 'recurring',
            'every', 'regular', 'routine'
        ]
        return any(indicator in content for indicator in recurring_indicators)
    
    def _estimate_prep_time(self, meeting_type: str, content: str) -> int:
        """Estimate preparation time needed in minutes."""
        prep_times = {
            'presentation': 45,
            'review': 30,
            'client_meeting': 30,
            'interview': 25,
            'planning': 20,
            'one_on_one': 15,
            'team_meeting': 10,
            'standup': 5,
            'general': 10
        }
        
        base_time = prep_times.get(meeting_type, 10)
        
        # Adjust based on content
        if 'quarterly' in content or 'annual' in content:
            base_time *= 2
        elif 'demo' in content or 'presentation' in content:
            base_time = max(base_time, 30)
        
        return base_time
    
    def _requires_materials(self, meeting_type: str, content: str) -> bool:
        """Check if meeting requires preparation materials."""
        material_indicators = [
            'presentation', 'slides', 'document', 'report', 'demo',
            'materials', 'handout', 'agenda'
        ]
        
        high_material_types = ['presentation', 'review', 'client_meeting']
        
        return (meeting_type in high_material_types or 
                any(indicator in content for indicator in material_indicators))
    
    def _create_prep_checklist(self, prep_level: str, content: str) -> List[str]:
        """Create a preparation checklist based on meeting needs."""
        checklist = []
        
        if prep_level == 'high':
            checklist.extend([
                "Review meeting agenda and objectives",
                "Prepare presentation materials if needed",
                "Research attendees and their backgrounds",
                "Gather relevant data and documents",
                "Test any technology/demos",
                "Prepare questions and talking points"
            ])
        elif prep_level == 'medium':
            checklist.extend([
                "Review meeting agenda",
                "Prepare key talking points",
                "Gather necessary documents",
                "Think about questions to ask"
            ])
        else:  # low
            checklist.extend([
                "Review meeting purpose",
                "Prepare brief status update"
            ])
        
        # Add specific items based on content
        if 'demo' in content:
            checklist.append("Test demo and backup plans")
        if 'data' in content or 'metrics' in content:
            checklist.append("Prepare relevant data and analytics")
        if 'decision' in content:
            checklist.append("Prepare recommendation and rationale")
        
        return checklist
    
    def _calculate_duration(self, event: Dict[str, Any]) -> int:
        """Calculate meeting duration in minutes."""
        start = event.get('start', {})
        end = event.get('end', {})
        
        try:
            if 'dateTime' in start and 'dateTime' in end:
                start_time = datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00'))
                end_time = datetime.fromisoformat(end['dateTime'].replace('Z', '+00:00'))
                duration = (end_time - start_time).total_seconds() / 60
                return int(duration)
        except:
            pass
        
        return 60  # Default 1 hour
    
    def _create_reminder_message(self, event: Dict[str, Any]) -> str:
        """Create a personalized reminder message."""
        summary = event.get('summary', 'Your meeting')
        prep_requirements = event.get('preparation_required', {})
        checklist = prep_requirements.get('preparation_checklist', [])
        
        message = f"Reminder: {summary} is coming up. "
        
        if checklist:
            message += f"Don't forget to: {', '.join(checklist[:3])}"
            if len(checklist) > 3:
                message += f" and {len(checklist) - 3} other items"
        
        return message
    
    def get_calendar_summary_data(self, days_ahead: int = 7) -> Dict[str, Any]:
        """Get comprehensive calendar data for AI summarization."""
        events = self.collect_meetings_with_prep_data(days_ahead)
        
        # Separate today's events and upcoming events
        today = datetime.now().date()
        today_events = []
        upcoming_events = []
        
        for event in events:
            event_date = self._get_event_date(event)
            if event_date and event_date == today:
                today_events.append(event)
            else:
                upcoming_events.append(event)
        
        return {
            'total_events': len(events),
            'today_events': today_events,
            'upcoming_events': upcoming_events[:10],  # Next 10 events
            'meetings_needing_prep': [e for e in events if e.get('preparation_required', {}).get('level') != 'low'],
            'high_importance_meetings': [e for e in events if e.get('importance_score', 5) >= 7],
            'collection_time': datetime.now().isoformat(),
            'meeting_types': self._get_meeting_type_distribution(events)
        }
    
    def _get_event_date(self, event: Dict[str, Any]) -> Optional[datetime.date]:
        """Extract date from event."""
        try:
            start = event.get('start', {})
            if 'dateTime' in start:
                return datetime.fromisoformat(start['dateTime'].replace('Z', '+00:00')).date()
            elif 'date' in start:
                return datetime.fromisoformat(start['date']).date()
        except:
            pass
        return None
    
    def _get_meeting_type_distribution(self, events: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of meeting types."""
        distribution = {}
        
        for event in events:
            meeting_type = event.get('meeting_analysis', {}).get('type', 'general')
            distribution[meeting_type] = distribution.get(meeting_type, 0) + 1
        
        return distribution
