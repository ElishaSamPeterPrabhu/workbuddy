"""
Gmail integration for WorkBuddy (Jarvis Assistant).

Provides Gmail API integration for email notifications and management.
"""

from typing import List, Dict, Any, Optional
import os
import pickle
import logging
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from core.storage import get_db_connection

# Gmail API scope
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 
          'https://www.googleapis.com/auth/gmail.modify']

logger = logging.getLogger(__name__)


class GmailIntegration:
    """Handles Gmail API integration for email notifications and management."""
    
    def __init__(self):
        """Initialize Gmail integration."""
        self.service = None
        self.creds = None
        self._authenticate()
        self._init_email_cache()
    
    def _init_email_cache(self):
        """Initialize email cache table in database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS email_cache (
                message_id TEXT PRIMARY KEY,
                subject TEXT,
                sender TEXT,
                snippet TEXT,
                timestamp TEXT,
                is_read BOOLEAN,
                is_important BOOLEAN,
                labels TEXT,
                thread_id TEXT,
                last_checked TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2."""
        creds_path = os.path.join(os.path.dirname(__file__), 'gmail_token.pickle')
        
        if os.path.exists(creds_path):
            with open(creds_path, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    os.path.join(os.path.dirname(__file__), 'credentials.json'),
                    SCOPES
                )
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(creds_path, 'wb') as token:
                pickle.dump(self.creds, token)
        
        self.service = build('gmail', 'v1', credentials=self.creds)
        logger.info("Gmail API authenticated successfully")
    
    def get_unread_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch unread emails from inbox.
        
        Args:
            max_results: Maximum number of emails to fetch
            
        Returns:
            List of email dictionaries with details
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread in:inbox',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
                    self._cache_email(email_data)
            
            return emails
            
        except HttpError as error:
            logger.error(f"An error occurred fetching emails: {error}")
            return []
    
    def get_important_emails(self, hours: int = 24) -> List[Dict[str, Any]]:
        """
        Fetch important/priority emails from the last N hours.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            List of important email dictionaries
        """
        try:
            # Calculate the timestamp for N hours ago
            after_timestamp = int((datetime.now() - timedelta(hours=hours)).timestamp())
            
            results = self.service.users().messages().list(
                userId='me',
                q=f'is:important after:{after_timestamp}',
                maxResults=20
            ).execute()
            
            messages = results.get('messages', [])
            emails = []
            
            for msg in messages:
                email_data = self._get_email_details(msg['id'])
                if email_data:
                    emails.append(email_data)
            
            return emails
            
        except HttpError as error:
            logger.error(f"An error occurred fetching important emails: {error}")
            return []
    
    def _get_email_details(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific email."""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id
            ).execute()
            
            # Extract headers
            headers = message['payload'].get('headers', [])
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), '')
            
            # Extract snippet and labels
            snippet = message.get('snippet', '')
            labels = message.get('labelIds', [])
            
            return {
                'id': message_id,
                'subject': subject,
                'sender': sender,
                'snippet': snippet,
                'timestamp': date,
                'is_read': 'UNREAD' not in labels,
                'is_important': 'IMPORTANT' in labels,
                'labels': labels,
                'thread_id': message.get('threadId', '')
            }
            
        except HttpError as error:
            logger.error(f"Error getting email details: {error}")
            return None
    
    def _cache_email(self, email_data: Dict[str, Any]):
        """Cache email data in local database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT OR REPLACE INTO email_cache 
            (message_id, subject, sender, snippet, timestamp, is_read, 
             is_important, labels, thread_id, last_checked)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            email_data['id'],
            email_data['subject'],
            email_data['sender'],
            email_data['snippet'],
            email_data['timestamp'],
            email_data['is_read'],
            email_data['is_important'],
            ','.join(email_data['labels']),
            email_data['thread_id'],
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
    
    def get_cached_unread_count(self) -> int:
        """Get count of unread emails from cache."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM email_cache WHERE is_read = 0")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def mark_as_read(self, message_id: str):
        """Mark an email as read."""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            # Update cache
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE email_cache SET is_read = 1 WHERE message_id = ?",
                (message_id,)
            )
            conn.commit()
            conn.close()
            
            logger.info(f"Marked email {message_id} as read")
            
        except HttpError as error:
            logger.error(f"Error marking email as read: {error}")
    
    def get_morning_email_summary(self) -> Dict[str, Any]:
        """Get email summary for morning briefing."""
        unread_emails = self.get_unread_emails(max_results=5)
        important_emails = self.get_important_emails(hours=12)
        
        return {
            'unread_count': len(unread_emails),
            'unread_emails': unread_emails[:3],  # Top 3 unread
            'important_count': len(important_emails),
            'important_emails': important_emails[:2],  # Top 2 important
            'total_cached_unread': self.get_cached_unread_count()
        } 