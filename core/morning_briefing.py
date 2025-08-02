"""
Morning Briefing module for WorkBuddy (Jarvis Assistant).

Provides a comprehensive morning briefing with weather, calendar, emails, and more.
"""

import os
import json
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from core.storage import get_db_connection, get_user_preference, set_user_preference
from integrations.calendar import GoogleCalendarIntegration
from integrations.gmail import GmailIntegration
from integrations.github import GitHubIntegration
from core.speech import VoiceSynthesizer
import threading

logger = logging.getLogger(__name__)


class MorningBriefing:
    """Orchestrates the morning briefing experience."""
    
    def __init__(self):
        """Initialize morning briefing components."""
        self.calendar = None
        self.gmail = None
        self.github = None
        self.voice = VoiceSynthesizer()
        self._init_integrations()
    
    def _init_integrations(self):
        """Initialize available integrations."""
        try:
            self.calendar = GoogleCalendarIntegration()
        except Exception as e:
            logger.warning(f"Calendar integration not available: {e}")
        
        try:
            self.gmail = GmailIntegration()
        except Exception as e:
            logger.warning(f"Gmail integration not available: {e}")
        
        try:
            self.github = GitHubIntegration()
        except Exception as e:
            logger.warning(f"GitHub integration not available: {e}")
    
    def get_weather(self, city: Optional[str] = None) -> Dict[str, Any]:
        """
        Get weather information (using free OpenWeatherMap API).
        
        Note: You'll need to sign up for a free API key at openweathermap.org
        """
        api_key = os.getenv('OPENWEATHER_API_KEY')
        if not api_key:
            # Use a demo response if no API key
            return {
                'temperature': '72°F',
                'condition': 'Partly Cloudy',
                'humidity': '65%',
                'forecast': 'Pleasant day ahead with mild temperatures'
            }
        
        city = city or get_user_preference('weather_city', 'New York')
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=imperial"
            response = requests.get(url, timeout=5)
            data = response.json()
            
            return {
                'temperature': f"{round(data['main']['temp'])}°F",
                'condition': data['weather'][0]['description'].title(),
                'humidity': f"{data['main']['humidity']}%",
                'forecast': f"Today will be {data['weather'][0]['description']} with a high of {round(data['main']['temp_max'])}°F"
            }
        except Exception as e:
            logger.error(f"Weather API error: {e}")
            return {
                'temperature': 'Unknown',
                'condition': 'Weather data unavailable',
                'humidity': 'Unknown',
                'forecast': 'Unable to fetch weather data'
            }
    
    def generate_morning_briefing(self) -> str:
        """Generate the complete morning briefing text."""
        hour = datetime.now().hour
        greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
        
        briefing_parts = [f"{greeting}! It's {datetime.now().strftime('%A, %B %d at %I:%M %p')}."]
        
        # Weather
        weather = self.get_weather()
        briefing_parts.append(
            f"The weather is {weather['condition']} with a temperature of {weather['temperature']}. "
            f"{weather['forecast']}."
        )
        
        # Calendar events
        if self.calendar:
            try:
                events = self.calendar.get_upcoming_events(max_results=5)
                if events:
                    briefing_parts.append(f"You have {len(events)} events today:")
                    for i, event in enumerate(events[:3]):  # Show first 3
                        start_time = datetime.fromisoformat(event['start_time']).strftime('%I:%M %p')
                        briefing_parts.append(f"- {event['summary']} at {start_time}")
                else:
                    briefing_parts.append("Your calendar is clear today.")
            except Exception as e:
                logger.error(f"Calendar error: {e}")
        
        # Email summary
        if self.gmail:
            try:
                email_summary = self.gmail.get_morning_email_summary()
                unread = email_summary['unread_count']
                if unread > 0:
                    briefing_parts.append(f"You have {unread} unread emails.")
                    for email in email_summary['unread_emails']:
                        sender = email['sender'].split('<')[0].strip()
                        briefing_parts.append(f"- From {sender}: {email['subject']}")
                else:
                    briefing_parts.append("Your inbox is all caught up!")
            except Exception as e:
                logger.error(f"Gmail error: {e}")
        
        # GitHub notifications
        if self.github:
            try:
                notifications = self.github.get_notifications()
                if notifications:
                    briefing_parts.append(f"You have {len(notifications)} GitHub notifications.")
            except Exception as e:
                logger.error(f"GitHub error: {e}")
        
        # Reminders
        reminders = self._get_todays_reminders()
        if reminders:
            briefing_parts.append(f"You have {len(reminders)} reminders set for today.")
        
        # Closing
        briefing_parts.append("How can I assist you today?")
        
        return " ".join(briefing_parts)
    
    def _get_todays_reminders(self) -> List[Dict[str, Any]]:
        """Get reminders scheduled for today."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        today_start = datetime.now().replace(hour=0, minute=0, second=0).isoformat()
        today_end = datetime.now().replace(hour=23, minute=59, second=59).isoformat()
        
        cursor.execute("""
            SELECT * FROM reminders 
            WHERE reminder_time BETWEEN ? AND ? 
            AND is_completed = 0
            ORDER BY reminder_time
        """, (today_start, today_end))
        
        reminders = cursor.fetchall()
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], reminder)) 
                for reminder in reminders]
    
    def deliver_briefing(self, callback=None):
        """Deliver the morning briefing with voice."""
        briefing_text = self.generate_morning_briefing()
        
        # Log the briefing
        logger.info(f"Morning briefing: {briefing_text}")
        
        # Store last briefing time
        set_user_preference('last_briefing', datetime.now().isoformat())
        
        # Deliver via voice in a separate thread
        def speak_briefing():
            self.voice.speak(briefing_text)
            if callback:
                callback(briefing_text)
        
        thread = threading.Thread(target=speak_briefing)
        thread.daemon = True
        thread.start()
        
        return briefing_text
    
    def should_deliver_briefing(self) -> bool:
        """Check if we should deliver the morning briefing."""
        # Check if briefing is enabled
        if not get_user_preference('morning_briefing_enabled', True):
            return False
        
        # Check time window (default: 7 AM - 10 AM)
        current_hour = datetime.now().hour
        start_hour = get_user_preference('briefing_start_hour', 7)
        end_hour = get_user_preference('briefing_end_hour', 10)
        
        if not (start_hour <= current_hour < end_hour):
            return False
        
        # Check if already delivered today
        last_briefing = get_user_preference('last_briefing')
        if last_briefing:
            last_date = datetime.fromisoformat(last_briefing).date()
            if last_date == datetime.now().date():
                return False
        
        return True 