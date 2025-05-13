"""
AI client module for WorkBuddy (Jarvis Assistant).

Handles communication with the AI backend for prompt-response interactions.

TODO: Move this module to /core/ai_client.py as per modular structure.
"""

import requests
import json
import os
import sys
import re
from datetime import datetime, timedelta
from core import scheduler
import dateparser
import dateutil.parser


class WorkflowState:
    """Helper class to structure data for the AI API call"""

    def __init__(self, user_query, retrieved_docs=None, file_details=None):
        self.user_query = user_query
        self.retrieved_docs = retrieved_docs or [Document()]
        self.file_details = file_details


class Document:
    """Simple document class for retrieved docs"""

    def __init__(self, page_content=""):
        self.page_content = page_content


class AIClient:
    def __init__(self, model_name="gpt-4o-mini"):
        self.model_name = model_name

        # Trimble API setup
        self.assistant_id = "iam-llmapi"
        self.base_url = f"https://agw.construction-integration.trimble.cloud/trimbledeveloperprogram/assistants/v1/agents/{self.assistant_id}/messages"
        self.access_token = os.environ.get(
            "TRIMBLE_API_TOKEN",
            "eyJhbGciOiJSUzI1NiIsImtpZCI6IjEiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL2lkLnRyaW1ibGUuY29tIiwiZXhwIjoxNzQ1MzM3MTcwLCJuYmYiOjE3NDUzMzM1NzAsImlhdCI6MTc0NTMzMzU3MCwianRpIjoiYzdhM2ZmMDkxMmRiNGI0MmEzMWE1MDVjZTNkZmMyNzgiLCJqd3RfdmVyIjoyLCJzdWIiOiIwYzhkOGUwZC02MDU4LTQ2MGItYjExYS0xYTExMjE4NmFkNjQiLCJhcHBsaWNhdGlvbl9uYW1lIjoicmVsZWFzZS1ub3RlcyIsImlkZW50aXR5X3R5cGUiOiJhcHBsaWNhdGlvbiIsImF1dGhfdGltZSI6MTc0NTMzMzU3MCwiYW1yIjpbImNsaWVudF9jcmVkZW50aWFscyJdLCJhdWQiOlsiMGM4ZDhlMGQtNjA1OC00NjBiLWIxMWEtMWExMTIxODZhZDY0Il0sInNjb3BlIjoicmVsZWFzZS1ub3RlcyJ9.nrMAYOvxhZC6FLK_qHlJAWgWyx6flmPzaRFdbOwMl1qsW4he-eJetSpk7F3YL4_crjVYDpXtiJcKqNb2j-p5Qd-bHz8SOsyk_5h_T1gGq7xJw697CuCnB0HG_7ARVyb9lxL56BWegOoC3cot2UmZlXPSbiowJ92lbDQ0JcUpoAlAWJSr6rx7OsblZjAsr3hmDIMv1iDGjO4OZwkoZZSw_XuMowgTbckGsCnpnyO8PlsxYTTYTE1OqTCoJIRCK_pkEcdc6jh3O-lTKS8NELIjocLaXNJbzyKm_01ifpMZNNmuXO6CwTm7cW4sGIE18q1s2wiD8JO8qYHDFVwf0AgBGA",
        )
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        # For session tracking
        self.session_id = "workbuddy_session"
        self.interlocutor_id = "workbuddy_user"

        # Simple fallback responses when no API connection is available
        self.fallback_responses = {
            "hello": "Hello! How can I help you today?",
            "hi": "Hi there! What can I do for you?",
            "how are you": "I'm functioning well, thank you! How can I assist you?",
            "help": "I can help you with various tasks like opening files, searching for information, or answering questions.",
            "bye": "Goodbye! Have a great day!",
            "thank you": "You're welcome! Is there anything else you need?",
            "thanks": "You're welcome! Is there anything else you need?",
            "who are you": "I'm WorkBuddy, your AI assistant for workplace productivity.",
            "what can you do": "I can help with opening applications, searching for information, answering questions, and more.",
        }

    def rag_qa(self, state):
        """Implementation of the Trimble API rag_qa logic"""
        try:
            # Prepare the message
            message = f"{state.user_query}"
            body = {
                "message": message,
                "session_id": self.session_id,
                "interlocutor_id": self.interlocutor_id,
                "stream": False,
                "model_id": self.model_name,
            }

            # Make the API request
            response = requests.post(
                self.base_url, headers=self.headers, data=json.dumps(body)
            )

            # Parse the response
            answer = ""
            if response.status_code == 200:
                answer = response.json()["message"]
            print(response.json())
            return {
                "file_details": state.file_details or {},
                "rag_answer": answer,
            }
        except Exception as e:
            print(f"Error in rag_qa: {str(e)}")
            return {"file_details": {}, "rag_answer": f"Error: {str(e)}"}

    def get_response(self, user_message):
        """Get a response from the AI model or generate a fallback response. Handles reminders."""

        # Check for 'remind me' command
        remind_match = re.match(
            r"remind me (in|at|on)? ?(.+)? to (.+)", user_message, re.IGNORECASE
        )
        if remind_match:
            time_part = remind_match.group(2) or ""
            message_part = remind_match.group(3) or ""
            # Parse the time using dateparser
            remind_time = dateparser.parse(
                time_part, settings={"PREFER_DATES_FROM": "future"}
            )
            if not remind_time:
                return (
                    "Sorry, I couldn't understand the reminder time. Please try again."
                )
            # If only a duration (e.g., 'in 10 minutes'), dateparser gives a datetime in the future
            if remind_time < datetime.now():
                return (
                    "The reminder time you specified is in the past. Please try again."
                )
            scheduler.schedule_reminder(message_part, remind_time)
            return f"Okay, I'll remind you to {message_part} at {remind_time.strftime('%Y-%m-%d %H:%M:%S')}."

        # Check if we need to handle a system command
        system_response = self.handle_system_command(user_message)
        if system_response:
            return system_response

        try:
            # Create a state object for the rag_qa function
            state = WorkflowState(
                user_query=user_message, retrieved_docs=[Document(page_content="")]
            )

            # Get response from the AI
            result = self.rag_qa(state)

            if result and result.get("rag_answer"):
                # After parsing response_json from the AI ...
                if (
                    isinstance(result, dict)
                    and result.get("is_reminder") is True
                    and result.get("reminder")
                ):
                    reminder = result["reminder"]
                    message = reminder.get("message")
                    remind_at = reminder.get("remind_at")
                    if message and remind_at:
                        # Parse ISO datetime string to datetime object
                        remind_at_dt = dateutil.parser.isoparse(remind_at)
                        scheduler.schedule_reminder(message, remind_at_dt)
                return result["rag_answer"]
            else:
                return self.get_fallback_response(user_message)

        except Exception as e:
            print(f"Exception in AI client: {str(e)}")
            return self.get_fallback_response(user_message)

    def get_fallback_response(self, user_message):
        """Generate a simple fallback response based on the user's message"""
        user_message = user_message.lower()

        # Check for exact matches in fallback responses
        for key, response in self.fallback_responses.items():
            if key in user_message:
                return response

        # Handle basic file operations
        if "open" in user_message and (
            "file" in user_message
            or "folder" in user_message
            or "directory" in user_message
        ):
            return "I'd be happy to help you open that, but I need to be properly configured first."

        # Handle search requests
        if (
            "search" in user_message
            or "find" in user_message
            or "look for" in user_message
        ):
            return "I can help you search for that once I'm properly set up with API access."

        # Default response
        return "I understand you want to know about that. Once I'm properly configured with API access, I'll be able to provide specific information."

    def handle_system_command(self, command):
        """Handle system-specific commands"""
        command = command.lower().strip()

        # Open applications
        if re.match(r"open (.*)", command):
            app_name = re.match(r"open (.*)", command).group(1).strip()
            return f"I'll try to open {app_name} for you once I have system access capabilities."

        # Search web
        if re.match(r"search (for )?(.*)", command) or "google" in command:
            query = re.sub(r"search (for )?|google", "", command).strip()
            return f"I'll search for '{query}' once I have web access capabilities."

        # No system command recognized
        return None
