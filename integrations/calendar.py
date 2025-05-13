"""
Google Calendar integration module for WorkBuddy (Jarvis Assistant).

Handles authentication, CRUD operations for calendar events, notifications for upcoming meetings, and daily meeting summaries.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime
import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

CONFIG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config")
CREDENTIALS_PATH = os.path.join(CONFIG_DIR, "credentials.json")
TOKEN_PATH = os.path.join(CONFIG_DIR, "token.pickle")
SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarIntegration:
    """
    Integration class for interacting with Google Calendar API.
    """

    def __init__(self) -> None:
        """
        Initialize the GoogleCalendarIntegration, handle authentication and token loading.
        """
        self.creds = None
        self.service = None
        if not os.path.exists(CONFIG_DIR):
            os.makedirs(CONFIG_DIR)
        self.authenticate()

    def authenticate(self) -> bool:
        """
        Authenticate with Google Calendar using OAuth2. Store and refresh tokens as needed.

        Returns:
            bool: True if authentication is successful, False otherwise.
        """
        try:
            creds = None
            # Load token if it exists
            if os.path.exists(TOKEN_PATH):
                with open(TOKEN_PATH, "rb") as token:
                    creds = pickle.load(token)
            # If no valid creds, do OAuth flow
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(CREDENTIALS_PATH):
                        print(f"Missing credentials.json at {CREDENTIALS_PATH}")
                        return False
                    flow = InstalledAppFlow.from_client_secrets_file(
                        CREDENTIALS_PATH, SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                # Save the token
                with open(TOKEN_PATH, "wb") as token:
                    pickle.dump(creds, token)
            self.creds = creds
            self.service = build("calendar", "v3", credentials=creds)
            return True
        except Exception as e:
            print(f"Google Calendar authentication error: {e}")
            return False

    def get_events(
        self, start: Optional[datetime] = None, end: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Fetch calendar events within a given time window.

        Args:
            start (Optional[datetime]): Start of the time window. Defaults to today.
            end (Optional[datetime]): End of the time window. Defaults to end of today.

        Returns:
            List[Dict[str, Any]]: List of event details.
        """
        if not self.service:
            if not self.authenticate():
                return []
        try:
            from datetime import timedelta
            import pytz

            tz = pytz.timezone(os.environ.get("TIMEZONE", "UTC"))
            now = datetime.now(tz)
            if not start:
                start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            if not end:
                end = start + timedelta(days=1)
            time_min = start.isoformat()
            time_max = end.isoformat()
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=time_min,
                    timeMax=time_max,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            return events
        except HttpError as error:
            print(f"An error occurred: {error}")
            return []
        except Exception as e:
            print(f"Google Calendar get_events error: {e}")
            return []

    def add_event(
        self,
        summary: str,
        start: datetime,
        end: datetime,
        description: Optional[str] = None,
        attendees: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Add a new event to the calendar.

        Args:
            summary (str): Event title.
            start (datetime): Event start time.
            end (datetime): Event end time.
            description (Optional[str]): Event description.
            attendees (Optional[List[str]]): List of attendee emails.

        Returns:
            Dict[str, Any]: Details of the created event or error info.
        """
        if not self.service:
            if not self.authenticate():
                return {"error": "Authentication failed"}
        try:
            event = {
                "summary": summary,
                "start": {"dateTime": start.isoformat()},
                "end": {"dateTime": end.isoformat()},
            }
            if description:
                event["description"] = description
            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]
            created_event = (
                self.service.events().insert(calendarId="primary", body=event).execute()
            )
            return created_event
        except Exception as e:
            print(f"Google Calendar add_event error: {e}")
            return {"error": str(e)}

    def update_event(self, event_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing calendar event.

        Args:
            event_id (str): The ID of the event to update.
            updates (Dict[str, Any]): Fields to update.

        Returns:
            Dict[str, Any]: Updated event details or error info.
        """
        if not self.service:
            if not self.authenticate():
                return {"error": "Authentication failed"}
        try:
            event = (
                self.service.events()
                .get(calendarId="primary", eventId=event_id)
                .execute()
            )
            event.update(updates)
            updated_event = (
                self.service.events()
                .update(calendarId="primary", eventId=event_id, body=event)
                .execute()
            )
            return updated_event
        except Exception as e:
            print(f"Google Calendar update_event error: {e}")
            return {"error": str(e)}

    def delete_event(self, event_id: str) -> bool:
        """
        Delete a calendar event by ID.

        Args:
            event_id (str): The ID of the event to delete.

        Returns:
            bool: True if deleted, False otherwise.
        """
        if not self.service:
            if not self.authenticate():
                return False
        try:
            self.service.events().delete(
                calendarId="primary", eventId=event_id
            ).execute()
            return True
        except Exception as e:
            print(f"Google Calendar delete_event error: {e}")
            return False

    def notify_upcoming_meetings(self, minutes_before: int = 10) -> None:
        """
        Notify the user before each meeting today, defaulting to 10 minutes before start.

        Args:
            minutes_before (int): Minutes before meeting to notify.
        """
        pass

    def daily_meeting_summary(self) -> str:
        """
        Generate and return a summary of today's meetings for morning/startup notification.

        Returns:
            str: Human-readable summary of today's meetings.
        """
        pass

    def describe_event(self, event: Dict[str, Any]) -> str:
        """
        Generate a short, AI-friendly description of a calendar event.

        Args:
            event (Dict[str, Any]): The event details.

        Returns:
            str: Description of the event.
        """
        pass
