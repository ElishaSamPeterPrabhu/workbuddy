"""
Enhanced Email Data Collector for WorkBuddy.
Collects and categorizes emails for AI processing.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from integrations.gmail import GmailIntegration
import re
from core.storage import get_db_connection

logger = logging.getLogger(__name__)


class EnhancedEmailCollector:
    """Enhanced email collection and categorization for AI processing."""
    
    def __init__(self):
        """Initialize the enhanced email collector."""
        try:
            self.gmail = GmailIntegration()
            self.initialized = True
            logger.info("Enhanced email collector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gmail integration: {e}")
            self.gmail = None
            self.initialized = False
    
    def collect_emails_with_context(self, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Collect emails with full context for AI processing.
        
        Args:
            hours_back: Number of hours to look back for emails
            
        Returns:
            List of emails with enhanced context data
        """
        if not self.initialized:
            logger.warning("Email collector not initialized")
            return []
        
        try:
            # Get recent emails
            emails = self.gmail.get_unread_emails(max_results=50)
            enhanced_emails = []
            
            for email in emails:
                enhanced_email = self._enhance_email_context(email)
                enhanced_emails.append(enhanced_email)
            
            logger.info(f"Collected {len(enhanced_emails)} emails with enhanced context")
            return enhanced_emails
            
        except Exception as e:
            logger.error(f"Error collecting emails: {e}")
            return []
    
    def _enhance_email_context(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Add context and intelligence to email data."""
        enhanced = email.copy()
        
        # Add sender importance scoring
        enhanced['sender_importance'] = self._calculate_sender_importance(email['sender'])
        
        # Detect meeting invitations
        enhanced['meeting_detection'] = self._detect_meeting_content(email.get('snippet', ''))
        
        # Extract task/action items
        enhanced['task_extraction'] = self._extract_tasks(email.get('snippet', ''))
        
        # Calculate urgency score
        enhanced['urgency_score'] = self._calculate_urgency(email)
        
        # Detect email type
        enhanced['email_type'] = self._classify_email_type(email)
        
        return enhanced
    
    def _calculate_sender_importance(self, sender: str) -> int:
        """
        Calculate sender importance (1-10 scale).
        
        Args:
            sender: Email sender string
            
        Returns:
            Importance score from 1-10
        """
        sender_lower = sender.lower()
        
        # High importance keywords
        high_keywords = ['ceo', 'manager', 'director', 'lead', 'senior', 'head']
        medium_keywords = ['team', 'project', 'coordinator', 'admin']
        
        # Domain-based scoring
        if any(domain in sender_lower for domain in ['noreply', 'no-reply', 'donotreply']):
            return 2
        
        # Keyword-based scoring
        if any(keyword in sender_lower for keyword in high_keywords):
            return 8
        elif any(keyword in sender_lower for keyword in medium_keywords):
            return 6
        
        # Default scoring
        return 5
    
    def _detect_meeting_content(self, content: str) -> Dict[str, Any]:
        """Detect if email contains meeting-related content."""
        content_lower = content.lower()
        
        meeting_keywords = [
            'meeting', 'call', 'conference', 'zoom', 'teams', 'hangout',
            'discuss', 'agenda', 'schedule', 'appointment', 'sync'
        ]
        
        time_patterns = [
            r'\d{1,2}:\d{2}\s*(am|pm)',  # 2:30 pm
            r'\d{1,2}\s*(am|pm)',        # 2 pm  
            r'at\s+\d{1,2}',             # at 2
            r'tomorrow', r'today', r'next week'
        ]
        
        has_meeting_keywords = any(keyword in content_lower for keyword in meeting_keywords)
        has_time_references = any(re.search(pattern, content_lower) for pattern in time_patterns)
        
        return {
            'is_meeting_related': has_meeting_keywords,
            'has_time_info': has_time_references,
            'confidence': 0.8 if (has_meeting_keywords and has_time_references) else 0.3
        }
    
    def _extract_tasks(self, content: str) -> List[Dict[str, Any]]:
        """Extract potential tasks and action items from email content."""
        content_lower = content.lower()
        tasks = []
        
        # Task-indicating phrases
        task_patterns = [
            r'please\s+(.{1,50})',
            r'can you\s+(.{1,50})',
            r'could you\s+(.{1,50})',
            r'need to\s+(.{1,50})',
            r'action required:\s*(.{1,50})',
            r'todo:\s*(.{1,50})',
            r'deadline:\s*(.{1,50})'
        ]
        
        for pattern in task_patterns:
            matches = re.finditer(pattern, content_lower, re.IGNORECASE)
            for match in matches:
                task_text = match.group(1).strip()
                if len(task_text) > 5:  # Filter out too short matches
                    tasks.append({
                        'text': task_text,
                        'type': 'action_required',
                        'confidence': 0.7
                    })
        
        return tasks[:5]  # Limit to top 5 tasks
    
    def _calculate_urgency(self, email: Dict[str, Any]) -> int:
        """Calculate email urgency score (1-10)."""
        score = 5  # Base score
        
        subject = email.get('subject', '').lower()
        snippet = email.get('snippet', '').lower()
        content = f"{subject} {snippet}"
        
        # Urgency indicators
        urgent_keywords = ['urgent', 'asap', 'immediate', 'emergency', 'critical', 'deadline']
        high_priority_keywords = ['important', 'priority', 'soon', 'today', 'tomorrow']
        
        # Increase score for urgent keywords
        if any(keyword in content for keyword in urgent_keywords):
            score += 3
        elif any(keyword in content for keyword in high_priority_keywords):
            score += 2
        
        # Check if marked as important
        if email.get('is_important', False):
            score += 2
        
        # Time sensitivity
        if any(word in content for word in ['today', 'tonight', 'this morning']):
            score += 2
        elif any(word in content for word in ['tomorrow', 'this week']):
            score += 1
        
        return min(score, 10)  # Cap at 10
    
    def _classify_email_type(self, email: Dict[str, Any]) -> str:
        """Classify email into categories."""
        subject = email.get('subject', '').lower()
        snippet = email.get('snippet', '').lower()
        sender = email.get('sender', '').lower()
        content = f"{subject} {snippet}"
        
        # Meeting invitations
        if email['meeting_detection']['is_meeting_related']:
            return 'meeting_invitation'
        
        # Automated emails
        if any(keyword in sender for keyword in ['noreply', 'no-reply', 'automated']):
            return 'automated'
        
        # Newsletters/marketing
        if any(keyword in content for keyword in ['unsubscribe', 'newsletter', 'marketing']):
            return 'newsletter'
        
        # Task/action emails
        if email.get('task_extraction') and len(email['task_extraction']) > 0:
            return 'task_request'
        
        # Calendar updates
        if any(keyword in content for keyword in ['calendar', 'event', 'invitation']):
            return 'calendar_update'
        
        # Information only
        if any(keyword in content for keyword in ['fyi', 'for your information', 'update']):
            return 'informational'
        
        # Default
        return 'general'
    
    def categorize_emails_for_ai(self, emails: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize emails for AI processing."""
        categories = {
            'urgent_action_required': [],
            'meeting_related': [],
            'task_requests': [],
            'informational': [],
            'calendar_updates': [],
            'automated': []
        }
        
        for email in emails:
            email_type = email.get('email_type', 'general')
            urgency = email.get('urgency_score', 5)
            
            # High urgency items
            if urgency >= 8:
                categories['urgent_action_required'].append(email)
            
            # Meeting related
            elif email_type == 'meeting_invitation' or email['meeting_detection']['is_meeting_related']:
                categories['meeting_related'].append(email)
            
            # Task requests
            elif email_type == 'task_request' or (email.get('task_extraction') and len(email['task_extraction']) > 0):
                categories['task_requests'].append(email)
            
            # Calendar updates
            elif email_type == 'calendar_update':
                categories['calendar_updates'].append(email)
            
            # Automated emails
            elif email_type == 'automated':
                categories['automated'].append(email)
            
            # Everything else is informational
            else:
                categories['informational'].append(email)
        
        # Sort each category by urgency
        for category in categories.values():
            category.sort(key=lambda x: x.get('urgency_score', 5), reverse=True)
        
        logger.info(f"Categorized emails: {[(k, len(v)) for k, v in categories.items()]}")
        return categories
    
    def get_email_summary_data(self) -> Dict[str, Any]:
        """Get comprehensive email data for AI summarization."""
        emails = self.collect_emails_with_context(hours_back=24)
        categorized = self.categorize_emails_for_ai(emails)
        
        return {
            'total_emails': len(emails),
            'categories': categorized,
            'collection_time': datetime.now().isoformat(),
            'top_senders': self._get_top_senders(emails),
            'urgency_distribution': self._get_urgency_distribution(emails)
        }
    
    def _get_top_senders(self, emails: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top email senders by count and importance."""
        sender_counts = {}
        sender_importance = {}
        
        for email in emails:
            sender = email.get('sender', 'Unknown')
            sender_counts[sender] = sender_counts.get(sender, 0) + 1
            sender_importance[sender] = max(
                sender_importance.get(sender, 0), 
                email.get('sender_importance', 5)
            )
        
        # Sort by combination of count and importance
        top_senders = sorted(
            sender_counts.items(), 
            key=lambda x: (x[1], sender_importance.get(x[0], 5)), 
            reverse=True
        )[:5]
        
        return [
            {
                'sender': sender,
                'count': count,
                'importance': sender_importance.get(sender, 5)
            }
            for sender, count in top_senders
        ]
    
    def _get_urgency_distribution(self, emails: List[Dict[str, Any]]) -> Dict[str, int]:
        """Get distribution of email urgency levels."""
        distribution = {'low': 0, 'medium': 0, 'high': 0, 'urgent': 0}
        
        for email in emails:
            urgency = email.get('urgency_score', 5)
            if urgency >= 8:
                distribution['urgent'] += 1
            elif urgency >= 6:
                distribution['high'] += 1
            elif urgency >= 4:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution
