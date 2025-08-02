"""
Outlook integration using MCP COM server for WorkBuddy.

Provides direct Outlook integration for enhanced calendar and email features.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from core.mcp_manager import mcp_manager

logger = logging.getLogger(__name__)


class OutlookMCPIntegration:
    """Direct Outlook integration using MCP COM server."""
    
    def __init__(self):
        self.outlook = None
        self.namespace = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize Outlook COM object via MCP."""
        try:
            # Check if COM server is available
            if "com-server" not in mcp_manager.servers:
                logger.warning("COM MCP server not available")
                return False
            
            # Create Outlook Application object
            self.outlook = await mcp_manager.call_tool("com-server", "CreateObject", {
                "progId": "Outlook.Application"
            })
            
            # Get MAPI namespace
            self.namespace = await mcp_manager.call_tool("com-server", "GetProperty", {
                "object": self.outlook,
                "property": "Session"
            })
            
            self._initialized = True
            logger.info("Outlook MCP integration initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Outlook MCP: {e}")
            return False
    
    async def get_calendar_items(self, days_ahead: int = 1) -> List[Dict[str, Any]]:
        """Get calendar items from Outlook for the specified number of days."""
        if not self._initialized:
            await self.initialize()
        
        if not self._initialized:
            return []
        
        try:
            # Get calendar folder
            calendar_folder = await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": self.namespace,
                "method": "GetDefaultFolder",
                "args": [9]  # olFolderCalendar = 9
            })
            
            # Get items collection
            items = await mcp_manager.call_tool("com-server", "GetProperty", {
                "object": calendar_folder,
                "property": "Items"
            })
            
            # Sort by start time
            await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": items,
                "method": "Sort",
                "args": ["[Start]"]
            })
            
            # Set date filter
            start_date = datetime.now().strftime("%m/%d/%Y")
            end_date = (datetime.now() + timedelta(days=days_ahead)).strftime("%m/%d/%Y")
            
            filter_string = f"[Start] >= '{start_date}' AND [Start] < '{end_date}'"
            
            # Apply filter
            await mcp_manager.call_tool("com-server", "SetProperty", {
                "object": items,
                "property": "IncludeRecurrences",
                "value": True
            })
            
            filtered_items = await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": items,
                "method": "Restrict",
                "args": [filter_string]
            })
            
            # Get count
            count = await mcp_manager.call_tool("com-server", "GetProperty", {
                "object": filtered_items,
                "property": "Count"
            })
            
            # Extract appointment details
            appointments = []
            for i in range(1, min(count + 1, 20)):  # Limit to 20 items
                item = await mcp_manager.call_tool("com-server", "InvokeMethod", {
                    "object": filtered_items,
                    "method": "Item",
                    "args": [i]
                })
                
                # Get appointment properties
                subject = await mcp_manager.call_tool("com-server", "GetProperty", {
                    "object": item,
                    "property": "Subject"
                })
                
                start = await mcp_manager.call_tool("com-server", "GetProperty", {
                    "object": item,
                    "property": "Start"
                })
                
                location = await mcp_manager.call_tool("com-server", "GetProperty", {
                    "object": item,
                    "property": "Location"
                })
                
                duration = await mcp_manager.call_tool("com-server", "GetProperty", {
                    "object": item,
                    "property": "Duration"
                })
                
                appointments.append({
                    'subject': subject or 'No Subject',
                    'start': start,
                    'location': location or '',
                    'duration': duration,
                    'source': 'Outlook'
                })
            
            return appointments
            
        except Exception as e:
            logger.error(f"Error getting Outlook calendar items: {e}")
            return []
    
    async def get_unread_emails(self, folder_name: str = "Inbox", 
                               max_items: int = 10) -> List[Dict[str, Any]]:
        """Get unread emails from specified Outlook folder."""
        if not self._initialized:
            await self.initialize()
        
        if not self._initialized:
            return []
        
        try:
            # Get inbox folder
            inbox = await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": self.namespace,
                "method": "GetDefaultFolder",
                "args": [6]  # olFolderInbox = 6
            })
            
            # Get items
            items = await mcp_manager.call_tool("com-server", "GetProperty", {
                "object": inbox,
                "property": "Items"
            })
            
            # Filter unread items
            unread_items = await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": items,
                "method": "Restrict",
                "args": ["[Unread] = True"]
            })
            
            # Sort by received time (newest first)
            await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": unread_items,
                "method": "Sort",
                "args": ["[ReceivedTime]", False]  # False = descending
            })
            
            # Get count
            count = await mcp_manager.call_tool("com-server", "GetProperty", {
                "object": unread_items,
                "property": "Count"
            })
            
            # Extract email details
            emails = []
            for i in range(1, min(count + 1, max_items + 1)):
                item = await mcp_manager.call_tool("com-server", "InvokeMethod", {
                    "object": unread_items,
                    "method": "Item",
                    "args": [i]
                })
                
                # Get email properties
                subject = await mcp_manager.call_tool("com-server", "GetProperty", {
                    "object": item,
                    "property": "Subject"
                })
                
                sender_name = await mcp_manager.call_tool("com-server", "GetProperty", {
                    "object": item,
                    "property": "SenderName"
                })
                
                body = await mcp_manager.call_tool("com-server", "GetProperty", {
                    "object": item,
                    "property": "Body"
                })
                
                received_time = await mcp_manager.call_tool("com-server", "GetProperty", {
                    "object": item,
                    "property": "ReceivedTime"
                })
                
                # Get first 200 chars of body
                preview = body[:200] + "..." if len(body) > 200 else body
                
                emails.append({
                    'subject': subject or 'No Subject',
                    'sender': sender_name,
                    'preview': preview.replace('\r\n', ' ').replace('\n', ' '),
                    'received': received_time,
                    'source': 'Outlook'
                })
            
            return emails
            
        except Exception as e:
            logger.error(f"Error getting Outlook emails: {e}")
            return []
    
    async def create_appointment(self, subject: str, start: datetime, 
                               duration: int = 60, location: str = "") -> bool:
        """Create a new appointment in Outlook calendar."""
        if not self._initialized:
            await self.initialize()
        
        if not self._initialized:
            return False
        
        try:
            # Create appointment item
            appointment = await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": self.outlook,
                "method": "CreateItem",
                "args": [1]  # olAppointmentItem = 1
            })
            
            # Set properties
            await mcp_manager.call_tool("com-server", "SetProperty", {
                "object": appointment,
                "property": "Subject",
                "value": subject
            })
            
            await mcp_manager.call_tool("com-server", "SetProperty", {
                "object": appointment,
                "property": "Start",
                "value": start.strftime("%m/%d/%Y %I:%M %p")
            })
            
            await mcp_manager.call_tool("com-server", "SetProperty", {
                "object": appointment,
                "property": "Duration",
                "value": duration
            })
            
            if location:
                await mcp_manager.call_tool("com-server", "SetProperty", {
                    "object": appointment,
                    "property": "Location",
                    "value": location
                })
            
            # Save appointment
            await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": appointment,
                "method": "Save"
            })
            
            logger.info(f"Created Outlook appointment: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating appointment: {e}")
            return False
    
    async def send_email(self, to: str, subject: str, body: str, 
                        attachments: Optional[List[str]] = None) -> bool:
        """Send an email using Outlook."""
        if not self._initialized:
            await self.initialize()
        
        if not self._initialized:
            return False
        
        try:
            # Create mail item
            mail = await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": self.outlook,
                "method": "CreateItem",
                "args": [0]  # olMailItem = 0
            })
            
            # Set properties
            await mcp_manager.call_tool("com-server", "SetProperty", {
                "object": mail,
                "property": "To",
                "value": to
            })
            
            await mcp_manager.call_tool("com-server", "SetProperty", {
                "object": mail,
                "property": "Subject",
                "value": subject
            })
            
            await mcp_manager.call_tool("com-server", "SetProperty", {
                "object": mail,
                "property": "Body",
                "value": body
            })
            
            # Add attachments if any
            if attachments:
                attachments_obj = await mcp_manager.call_tool("com-server", "GetProperty", {
                    "object": mail,
                    "property": "Attachments"
                })
                
                for attachment in attachments:
                    await mcp_manager.call_tool("com-server", "InvokeMethod", {
                        "object": attachments_obj,
                        "method": "Add",
                        "args": [attachment]
                    })
            
            # Send email
            await mcp_manager.call_tool("com-server", "InvokeMethod", {
                "object": mail,
                "method": "Send"
            })
            
            logger.info(f"Sent email to {to}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False 